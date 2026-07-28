"""Judge model wrapper — grades model outputs against scenario criteria."""

import os
from enum import StrEnum
from typing import Final, Protocol, assert_never

from benchmark.models import Scenario

ENV_JUDGE_MODEL: Final = "DOJO_JUDGE_MODEL"
ENV_API_KEY: Final = "DOJO_API_KEY"
ENV_JUDGE_MODE: Final = "DOJO_JUDGE_MODE"

_DEFAULT_JUDGE_MODEL: Final = "claude-sonnet-4-6"
_DEFAULT_JUDGE_MODE: Final = "simple"


class _JudgeMode(StrEnum):
    SIMPLE = "simple"
    LLM = "llm"

_JUDGE_SYSTEM_PROMPT: Final = """You are a strict judge evaluating AI model outputs.
Evaluate the following output against the criteria.
Respond with a JSON object: {"passed": true/false, "score": 0.0-1.0, "feedback": "explanation"}.
Be strict — partial credit must be justified."""


class JudgeResult(Protocol):
    """Protocol for judge grade result."""
    passed: bool
    score: float
    feedback: str


class JudgeModel:
    """Abstract judge model wrapper.

    Two modes controlled by DOJO_JUDGE_MODE env var:
    - "simple": substring matching against expected_behaviors
    - "llm":  calls a model API to evaluate
    """

    def __init__(
        self,
        judge_model: str | None = None,
        api_key: str | None = None,
        mode: str | None = None,
    ) -> None:
        self.judge_model = judge_model or os.environ.get(ENV_JUDGE_MODEL, _DEFAULT_JUDGE_MODEL)
        self.api_key = api_key or os.environ.get(ENV_API_KEY, "")
        raw = (mode or os.environ.get(ENV_JUDGE_MODE, _DEFAULT_JUDGE_MODE)).lower()
        self.mode = str(_JudgeMode(raw))

    async def grade(
        self,
        scenario: Scenario,
        output: str,
    ) -> dict:
        """Grade a single output. Returns {passed, score, feedback}."""
        match _JudgeMode(self.mode):
            case _JudgeMode.SIMPLE:
                return self._grade_simple(scenario, output)
            case _JudgeMode.LLM:
                return await self._grade_llm(scenario, output)
            case unreachable:
                assert_never(unreachable)

    async def grade_batch(
        self,
        results: list[tuple[Scenario, str]],
    ) -> list[dict]:
        """Grade a batch of (scenario, output) pairs."""
        verdicts: list[dict] = []
        for scenario, output in results:
            verdict = await self.grade(scenario, output)
            verdicts.append(verdict)
        return verdicts

    def _grade_simple(self, scenario: Scenario, output: str) -> dict:
        """Simple substring-matching judge — checks expected_behaviors."""
        output_lower = output.lower()
        matched = 0
        total = len(scenario.expected_behaviors)

        for behavior in scenario.expected_behaviors:
            if behavior.lower().strip() in output_lower:
                matched += 1

        if total == 0:
            passed = bool(output.strip())
            score = 1.0 if passed else 0.0
            feedback = "No expected behaviors defined; check based on non-empty output."
        else:
            score = matched / total
            passed = score >= 0.5
            feedback = (
                f"Simple judge: {matched}/{total} expected behaviors matched "
                f"(threshold: >=50%). Score: {score:.2f}"
            )

        return {"passed": passed, "score": score, "feedback": feedback}

    async def _grade_llm(self, scenario: Scenario, output: str) -> dict:
        """LLM-based judging — uses a model API to evaluate output quality."""
        from benchmark.runner import AgentHarness, AgentError

        judge_prompt = self._build_judge_prompt(scenario, output)
        harness = AgentHarness(
            model=self.judge_model,
            api_key=self.api_key,
        )

        try:
            raw = await harness.invoke(judge_prompt, system_prompt=_JUDGE_SYSTEM_PROMPT)
        except AgentError as e:
            return {
                "passed": False,
                "score": 0.0,
                "feedback": f"Judge API error: {e}",
            }
        finally:
            await harness.close()

        return self._parse_judge_response(raw)

    def _build_judge_prompt(self, scenario: Scenario, output: str) -> str:
        """Build the prompt for the LLM judge."""
        criteria_bullets = "\n".join(f"- {c}" for c in scenario.judge_criteria)
        expected_bullets = "\n".join(f"- {b}" for b in scenario.expected_behaviors)

        return f"""Scenario: {scenario.name}
Description: {scenario.description}

Expected Behaviors:
{expected_bullets}

Judge Criteria:
{criteria_bullets}

Maximum Score: {scenario.max_score}

--- Model Output ---
{output}
--- End Output ---

Evaluate this output against the criteria and expected behaviors.
Return JSON: {"passed": true/false, "score": <0.0-{scenario.max_score}>, "feedback": "explanation"}"""

    def _parse_judge_response(self, raw: str) -> dict:
        """Parse JSON response from the LLM judge."""
        import json

        try:
            start = raw.index("{")
            end = raw.rindex("}") + 1
            body = raw[start:end]
            result = json.loads(body)
            return {
                "passed": bool(result.get("passed", False)),
                "score": float(result.get("score", 0.0)),
                "feedback": str(result.get("feedback", raw[:200])),
            }
        except (ValueError, json.JSONDecodeError):
            return {
                "passed": False,
                "score": 0.0,
                "feedback": f"Failed to parse judge response: {raw[:200]}",
            }
