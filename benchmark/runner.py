"""Agent harness — calls the evaluated model via OpenAI-compatible API."""

import hashlib
import os
import sqlite3
import threading
import time
from pathlib import Path
from typing import Final

import httpx

# Env var keys
ENV_MODEL: Final = "DOJO_MODEL"
ENV_API_KEY: Final = "DOJO_API_KEY"
ENV_API_BASE: Final = "DOJO_API_BASE"
ENV_CACHE_DIR: Final = "DOJO_CACHE_DIR"

_DEFAULT_MODEL: Final = "deepseek-v4-flash"
_DEFAULT_BASE: Final = "https://api.deepseek.com/v1"
_DEFAULT_TIMEOUT: Final = 120.0


def _get_env(key: str, default: str) -> str:
    return os.environ.get(key, default)


class ResponseCache:
    """SQLite-backed LLM response cache. Keyed by SHA256 of model+messages."""

    def __init__(self, cache_dir: str | None = None) -> None:
        cache_dir = cache_dir or _get_env(ENV_CACHE_DIR, "") or "benchmark/cache"
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        self.db_path = os.path.join(cache_dir, "responses.db")
        self._local = threading.local()
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self._local.conn = sqlite3.connect(self.db_path)
            self._local.conn.execute("PRAGMA journal_mode=WAL")
        return self._local.conn

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS responses ("
            "  key TEXT PRIMARY KEY,"
            "  model TEXT NOT NULL,"
            "  prompt TEXT NOT NULL,"
            "  system_prompt TEXT NOT NULL DEFAULT '',"
            "  response TEXT NOT NULL,"
            "  created_at TEXT NOT NULL DEFAULT (datetime('now'))"
            ")"
        )
        conn.commit()
        conn.close()

    @staticmethod
    def _make_key(model: str, prompt: str, system_prompt: str) -> str:
        raw = f"{model}||{system_prompt}||{prompt}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, model: str, prompt: str, system_prompt: str = "") -> str | None:
        key = self._make_key(model, prompt, system_prompt)
        conn = self._get_conn()
        row = conn.execute(
            "SELECT response FROM responses WHERE key = ?", (key,)
        ).fetchone()
        return row[0] if row else None

    def set(self, model: str, prompt: str, system_prompt: str, response: str) -> None:
        key = self._make_key(model, prompt, system_prompt)
        conn = self._get_conn()
        conn.execute(
            "INSERT OR REPLACE INTO responses (key, model, prompt, system_prompt, response) "
            "VALUES (?, ?, ?, ?, ?)",
            (key, model, prompt, system_prompt, response),
        )
        conn.commit()


class AgentHarness:
    """Harness that calls an OpenAI-compatible model API with response caching."""

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        api_base: str | None = None,
        timeout: float = _DEFAULT_TIMEOUT,
        cache: ResponseCache | None = None,
    ) -> None:
        self.model = model or _get_env(ENV_MODEL, _DEFAULT_MODEL)
        self.api_key = api_key or _get_env(ENV_API_KEY, "")
        self.api_base = (api_base or _get_env(ENV_API_BASE, _DEFAULT_BASE)).rstrip("/")
        self.timeout = timeout
        self._cache = cache or (ResponseCache() if _get_env(ENV_CACHE_DIR, "") else ResponseCache())
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
        cached = self._cache.get(self.model, prompt, system_prompt)
        if cached is not None:
            return cached

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
            self._cache.set(self.model, prompt, system_prompt, content)
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
