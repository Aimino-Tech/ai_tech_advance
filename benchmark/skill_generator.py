"""Extract failure patterns from evaluation results and generate SKILL.md patches.

This is the distillation engine: it analyzes failed scenarios, identifies
common failure themes, and produces SKILL.md files that teach the model
to avoid those failures in future iterations.
"""

import json
import re
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Final

from benchmark.models import ScenarioResult

_SKILLS_DIR: Final = Path(__file__).resolve().parent.parent / "skills"
_GENERATED_DIR: Final = _SKILLS_DIR / "generated"
_TRACES_DIR: Final = Path(__file__).resolve().parent.parent / "traces"


class SkillGenerator:
    """Extract failure patterns from evaluation results and generate skill patches."""

    def extract_failure_patterns(self, failures: list[ScenarioResult]) -> list[dict]:
        """Analyze failed scenarios and return common failure patterns.

        Each pattern dict contains:
          - pattern: short label (e.g. "syntax_errors")
          - count: how many failures match
          - examples: list of scenario_id + excerpts from judge_feedback
          - common_theme: natural-language description
          - suggested_fix: what a skill patch should teach
        """
        if not failures:
            return []

        patterns: list[dict] = []
        feedbacks = [f.judge_feedback for f in failures if f.judge_feedback]
        errors = [f.error for f in failures if f.error]

        # 1. Pattern: API / harness errors
        api_failures = [f for f in failures if f.error]
        if api_failures:
            error_counts: Counter[str] = Counter()
            for f in api_failures:
                key = self._classify_error(f.error or "")
                error_counts[key] += 1
            top_error = error_counts.most_common(1)[0][0] if error_counts else "unknown"
            patterns.append({
                "pattern": "api_or_harness_error",
                "count": len(api_failures),
                "examples": [
                    {"scenario_id": f.scenario_id, "error": f.error}
                    for f in api_failures[:3]
                ],
                "common_theme": (
                    f"Model API errors: {error_counts.most_common(1)[0][0]} "
                    f"appeared {error_counts.most_common(1)[0][1]} times. "
                    f"Total {len(api_failures)} scenarios failed due to API issues."
                ),
                "suggested_fix": "Ensure API key is set, model is available, and timeout is sufficient.",
            })

        # 2. Pattern: scoring below 50% threshold
        low_score_failures = [
            f for f in failures
            if not f.error and f.score < 0.5
        ]
        if low_score_failures:
            patterns.append({
                "pattern": "low_quality_output",
                "count": len(low_score_failures),
                "examples": [
                    {
                        "scenario_id": f.scenario_id,
                        "score": f.score,
                        "feedback": (f.judge_feedback or "")[:200],
                    }
                    for f in low_score_failures[:3]
                ],
                "common_theme": (
                    f"{len(low_score_failures)} scenarios scored below 0.5. "
                    "Outputs partially met criteria but missed key expected behaviors."
                ),
                "suggested_fix": (
                    "Emphasize following all expected_behaviors strictly. "
                    "Teach the model to check each criterion before finalizing output."
                ),
            })

        # 3. Pattern: judge feedback mentions missing content
        missing_content = self._filter_by_keywords(failures, [
            "missing", "not found", "does not contain", "absent",
            "expected.*but", "should include", "failed to",
        ])
        if missing_content:
            patterns.append({
                "pattern": "missing_expected_content",
                "count": len(missing_content),
                "examples": [
                    {
                        "scenario_id": f.scenario_id,
                        "feedback": (f.judge_feedback or "")[:200],
                    }
                    for f in missing_content[:3]
                ],
                "common_theme": (
                    f"{len(missing_content)} scenarios failed because the output "
                    "was missing expected content or behaviors."
                ),
                "suggested_fix": (
                    "After writing output, verify each expected_behavior "
                    "is explicitly addressed. Do not assume implicit coverage."
                ),
            })

        # 4. Pattern: judge feedback mentions incorrect output
        incorrect_output = self._filter_by_keywords(failures, [
            "incorrect", "wrong", "error", "invalid", "does not work",
            "compil", "runtime error", "exception", "syntax error",
        ])
        if incorrect_output:
            patterns.append({
                "pattern": "incorrect_or_broken_output",
                "count": len(incorrect_output),
                "examples": [
                    {
                        "scenario_id": f.scenario_id,
                        "feedback": (f.judge_feedback or "")[:200],
                    }
                    for f in incorrect_output[:3]
                ],
                "common_theme": (
                    f"{len(incorrect_output)} scenarios produced functionally "
                    "incorrect output — compilation errors, runtime failures, "
                    "or wrong results."
                ),
                "suggested_fix": (
                    "Before submitting, verify the output compiles/runs correctly. "
                    "Test edge cases. Pay attention to language-specific syntax and semantics."
                ),
            })

        # 5. Overall summary if no specific patterns
        if not patterns:
            patterns.append({
                "pattern": "general_failure",
                "count": len(failures),
                "examples": [
                    {"scenario_id": f.scenario_id, "score": f.score}
                    for f in failures[:3]
                ],
                "common_theme": f"{len(failures)} scenarios failed with no clear pattern.",
                "suggested_fix": "Review all judge_criteria more carefully before writing output.",
            })

        return patterns

    def generate_skill_patch(self, patterns: list[dict], skill_name: str = "auto-trained") -> str:
        """Generate a SKILL.md file that addresses the failure patterns."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Build the core instructions from patterns
        instructions: list[str] = []
        for p in patterns:
            fix = p.get("suggested_fix", "")
            theme = p.get("common_theme", "")
            count = p.get("count", 0)
            pattern = p.get("pattern", "unknown")
            instructions.append(
                f"### {count}x {pattern.replace('_', ' ').title()}\n\n"
                f"{theme}\n\n"
                f"**Fix**: {fix}"
            )

        skill_body = "\n\n".join(instructions)

        return f"""---
name: {skill_name}
description: Auto-generated skill patch targeting {len(patterns)} failure patterns from training at {now}
iteration: auto
generated_at: {now}
---

# /{skill_name}

Auto-generated skill patch from training iteration.

## Failure Patterns Addressed

{skill_body}

## Expected Behaviors

When responding to prompts in the evaluated domain:

1. Read each expected_behavior explicitly before writing output.
2. Verify your output satisfies every expected_behavior and judge_criterion.
3. If you are unsure about a criterion, address it explicitly rather than skipping it.
4. After writing, re-read your output and confirm correctness — do not assume.
5. For code output: ensure it compiles, handles errors, and covers edge cases.

## Priority Rules

- Correctness over brevity: a complete correct answer is better than a short wrong one.
- Explicit over implicit: if a criterion asks for something, show it clearly.
- Verified over assumed: test your output mentally before presenting it.
"""

    def curriculum_from_traces(self, traces: list[dict], course_name: str) -> str:
        """Generate a dojo.md curriculum YAML from Fable 5 traces.

        Each trace dict should contain:
          - id: str
          - title: str
          - description: str
          - tags: list[str]
          - difficulty: str (default 'smoke')
          - prompt: str
          - expected_behaviors: list[str]
          - judge_criteria: list[str]
        """
        if not traces:
            return ""

        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        title = course_name.replace("-", " ").title()
        scenarios_yaml: list[str] = []

        for t in traces:
            tid = t.get("id", str(uuid.uuid4())[:8])
            tname = t.get("title", "Untitled Scenario")
            tdesc = t.get("description", "")
            tdifficulty = t.get("difficulty", "smoke")
            ttags = t.get("tags", [])
            tprompt = t.get("prompt", "")
            tbehaviors = t.get("expected_behaviors", [])
            tcriteria = t.get("judge_criteria", [])

            # Escape YAML special characters in prompt
            prompt_lines = tprompt.strip().split("\n")
            prompt_yaml = "\n".join(f"      {line}" if line else ""
                                    for line in prompt_lines)

            tags_yaml = ", ".join(f"{tag}" for tag in ttags)
            behaviors_yaml = "\n".join(f'      - "{b}"' for b in tbehaviors)
            criteria_yaml = "\n".join(f'      - "{c}"' for c in tcriteria)

            scenarios_yaml.append(f"""  - id: {tid}
    name: "{tname}"
    description: "{tdesc}"
    tags: [{tags_yaml}]
    difficulty: {tdifficulty}
    prompt: |
{prompt_yaml}
    expected_behaviors:
{behaviors_yaml}
    judge_criteria:
{criteria_yaml}""")

        return f"""---
course: {course_name}
title: {title}
description: Curriculum auto-generated from traces at {now}
difficulty: smoke
model: deepseek-v4-flash
scenarios:

{chr(10).join(scenarios_yaml)}
---
"""

    # --- helpers ---

    def _classify_error(self, error: str) -> str:
        """Classify an error message into a short label."""
        error_lower = error.lower()
        if "401" in error or "unauthorized" in error_lower or "api key" in error_lower:
            return "authentication_error"
        if "429" in error or "rate limit" in error_lower or "too many requests" in error_lower:
            return "rate_limit"
        if "500" in error or "503" in error or "server error" in error_lower:
            return "server_error"
        if "timeout" in error_lower or "timed out" in error_lower:
            return "timeout"
        if "404" in error or "not found" in error_lower:
            return "not_found"
        if "connection" in error_lower or "refused" in error_lower or "dns" in error_lower:
            return "connection_error"
        return "unknown_api_error"

    def _filter_by_keywords(
        self,
        failures: list[ScenarioResult],
        keywords: list[str],
    ) -> list[ScenarioResult]:
        """Return failures whose judge_feedback matches any keyword regex."""
        results: list[ScenarioResult] = []
        for f in failures:
            feedback = f.judge_feedback or ""
            for kw in keywords:
                if re.search(kw, feedback, re.IGNORECASE):
                    results.append(f)
                    break
        return results


def load_traces_from_dir(traces_dir: str | Path = _TRACES_DIR) -> list[dict]:
    """Load Fable 5 traces from trace directory.

    Scans for .json and .jsonl files. Each file should contain
    a list of trace objects or one trace object per line (jsonl).
    """
    traces_dir = Path(traces_dir)
    if not traces_dir.exists():
        return []

    traces: list[dict] = []
    for path in sorted(traces_dir.iterdir()):
        if path.suffix == ".json":
            try:
                data = json.loads(path.read_text())
                if isinstance(data, list):
                    traces.extend(data)
                else:
                    traces.append(data)
            except (json.JSONDecodeError, OSError):
                pass
        elif path.suffix == ".jsonl":
            try:
                for line in path.read_text().strip().split("\n"):
                    if line.strip():
                        traces.append(json.loads(line))
            except (json.JSONDecodeError, OSError):
                pass
    return traces


def save_skill_patch(
    content: str,
    iteration: int,
    output_dir: str | Path = _GENERATED_DIR,
) -> Path:
    """Write a generated SKILL.md to the output directory."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"iteration-{iteration:03d}"
    skill_dir = output_dir / filename
    skill_dir.mkdir(exist_ok=True)
    path = skill_dir / "SKILL.md"
    path.write_text(content)
    return path
