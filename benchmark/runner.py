"""Agent harness — calls the evaluated model via OpenAI-compatible API."""

import os
import time
from typing import Final

import httpx

# Env var keys
ENV_MODEL: Final = "DOJO_MODEL"
ENV_API_KEY: Final = "DOJO_API_KEY"
ENV_API_BASE: Final = "DOJO_API_BASE"

_DEFAULT_MODEL: Final = "deepseek-v4-flash"
_DEFAULT_BASE: Final = "https://api.deepseek.com/v1"
_DEFAULT_TIMEOUT: Final = 120.0


def _get_env(key: str, default: str) -> str:
    return os.environ.get(key, default)


class AgentHarness:
    """Harness that calls an OpenAI-compatible model API."""

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        api_base: str | None = None,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> None:
        self.model = model or _get_env(ENV_MODEL, _DEFAULT_MODEL)
        self.api_key = api_key or _get_env(ENV_API_KEY, "")
        self.api_base = (api_base or _get_env(ENV_API_BASE, _DEFAULT_BASE)).rstrip("/")
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.api_base,
                timeout=httpx.Timeout(self.timeout),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
        return self._client

    async def invoke(self, prompt: str, system_prompt: str = "") -> str:
        """Call the model and return the response text."""
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.0,
        }

        client = await self._get_client()
        start = time.monotonic()
        try:
            resp = await client.post("/chat/completions", json=payload)
            resp.raise_for_status()
            data = resp.json()
            elapsed = time.monotonic() - start
            choice = data["choices"][0]
            content: str = choice["message"]["content"]
            return content
        except httpx.HTTPStatusError as e:
            elapsed = time.monotonic() - start
            raise AgentError(
                status_code=e.response.status_code,
                body=e.response.text,
                elapsed=elapsed,
            ) from e
        except httpx.RequestError as e:
            elapsed = time.monotonic() - start
            raise AgentError(
                status_code=0,
                body=str(e),
                elapsed=elapsed,
            ) from e

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None


class AgentError(Exception):
    """Raised when the model API call fails."""

    def __init__(
        self,
        status_code: int,
        body: str,
        elapsed: float,
    ) -> None:
        self.status_code = status_code
        self.body = body
        self.elapsed = elapsed
        super().__init__(f"Agent API error [{status_code}] after {elapsed:.1f}s: {body[:200]}")
