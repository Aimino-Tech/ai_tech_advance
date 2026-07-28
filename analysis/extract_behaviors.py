"""Behavioral signature analysis from Fable 5 traces.

Mirrors fable5res DEEP_STATS.json behavioral_signatures section.
Detects self-correction patterns, hypothesis-driven debugging,
step coverage (ACKNOWLEDGE → SCOPE → GATHER → PLAN → EXECUTE →
VERIFY → ITERATE), and step transition matrices.
"""

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List

from typing import Any

from analysis.loader import TraceDict

# ── Step definitions ─────────────────────────────────────────────

STEPS: list[str] = [
    "ACKNOWLEDGE",
    "SCOPE",
    "GATHER",
    "PLAN",
    "EXECUTE",
    "VERIFY",
    "ITERATE",
]

# Patterns that identify each step from CoT text
STEP_PATTERNS: dict[str, list[str]] = {
    "ACKNOWLEDGE": [
        "i understand",
        "i see",
        "let me look",
        "let me check",
        "i'll start",
        "okay",
        "alright",
        "so we have",
        "the task is",
        "given",
        "looking at",
    ],
    "SCOPE": [
        "the problem",
        "issue is",
        "need to figure",
        "root cause",
        "what's happening",
        "investigate",
        "scope",
        "i need to determine",
        "let me understand what",
        "first i need",
    ],
    "GATHER": [
        "let me read",
        "let me look at",
        "let me check",
        "let me see",
        "i'll look at",
        "i'll check",
        "i'll examine",
        "let me examine",
        "let me find",
        "exploring",
        "i need to find",
        "let me gather",
        "searching",
        "let me search",
    ],
    "PLAN": [
        "my plan",
        "i'll",
        "first",
        "then",
        "approach",
        "strategy",
        "steps",
        "plan",
        "here's what",
        "i will",
        "let me start",
        "going to",
    ],
    "EXECUTE": [
        "let me try",
        "let me run",
        "let me execute",
        "let me fix",
        "let me update",
        "let me modify",
        "let me add",
        "i'll implement",
        "i'll write",
        "i'll create",
        "i'll edit",
        "i'll fix",
        "i'll add",
        "i'll update",
        "now i",
        "executing",
    ],
    "VERIFY": [
        "let me verify",
        "let me test",
        "let me check",
        "let me confirm",
        "let me validate",
        "let me run",
        "i'll test",
        "i'll verify",
        "i'll check",
        "test that",
        "verify",
        "make sure",
        "ensure",
        "validate",
        "confirm",
    ],
    "ITERATE": [
        "not quite",
        "doesn't work",
        "not working",
        "still fails",
        "that didn't work",
        "let me try again",
        "let me fix",
        "let me adjust",
        "let me revise",
        "i need to fix",
        "issue is",
        "problem is",
        "another approach",
        "different approach",
        "try something else",
        "instead i'll",
    ],
}

# Self-correction and debug patterns
SELF_CORRECTION_RE = re.compile(
    r"(actually|however|wait|no|instead|rather|"
    r"let me reconsider|on second thought|"
    r"hold on|that'?s not right|i made a mistake|"
    r"i was wrong|let me think again)",
    re.IGNORECASE,
)

HYPOTHESIS_RE = re.compile(
    r"(maybe|perhaps|could it be|might be|could be|"
    r"let me check if|i suspect|i think it'?s because|"
    r"likely due to|probably because|hypothesis)",
    re.IGNORECASE,
)

DEBUG_INVESTIGATE_RE = re.compile(
    r"(let me check|let me see|let me look|let me examine|"
    r"i'll check|i'll look|i'll examine|i'll investigate|"
    r"need to find|need to check|need to figure)",
    re.IGNORECASE,
)


# ── Dataclasses ──────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class BehaviorStats:
    """Aggregated behavioral signature statistics."""

    total_traces: int = 0

    # Self-correction
    self_correction_rate: float = 0.0
    avg_self_corrections: float = 0.0

    # Hypothesis-driven debugging
    hypothesis_driven_rate: float = 0.0
    avg_hypotheses: float = 0.0

    # Multi-step investigation (3+ investigation steps before fix)
    multi_investigation_rate: float = 0.0

    # Step coverage
    step_coverage: Dict[str, float] = field(default_factory=dict)
    step_transition_matrix: Dict[str, Dict[str, float]] = field(default_factory=dict)

    # Same-turn fix attempts
    same_turn_fix_rate: float = 0.0


@dataclass(frozen=True, slots=True)
class StepSequence:
    """Detected sequence of steps in a trace."""

    steps: tuple[str, ...] = ()
    transitions: tuple[tuple[str, str], ...] = ()


# ── Detection functions ──────────────────────────────────────────


def detect_self_correction(cot: str) -> int:
    """Count self-correction markers in CoT text."""
    if not cot:
        return 0
    return len(SELF_CORRECTION_RE.findall(cot))


def classify_step(cot_segment: str) -> str | None:
    """Classify a segment of CoT text into a step category.

    Returns the step name (e.g. 'ACKNOWLEDGE') or None if no step
    pattern matches.
    """
    if not cot_segment or not cot_segment.strip():
        return None

    segment_lower = cot_segment.lower()

    # Score each step by pattern match count
    scores: dict[str, int] = {}
    for step, patterns in STEP_PATTERNS.items():
        score = 0
        for pattern in patterns:
            if pattern in segment_lower:
                score += 1
        if score > 0:
            scores[step] = score

    if not scores:
        return None

    # Return highest-scoring step
    return max(scores, key=scores.get)


def detect_debug_pattern(trace: TraceDict) -> dict[str, Any]:
    """Detect debugging behavior patterns in a trace.

    Returns a dict with keys:
    - self_correction_count: int
    - hypothesis_count: int
    - investigation_steps: int
    - has_fix_attempt: bool
    - has_verification: bool
    """
    cot = trace.get("cot", "")
    output = trace.get("output", "")

    self_correction_count = detect_self_correction(cot)
    hypothesis_count = len(HYPOTHESIS_RE.findall(cot))
    investigation_steps = len(DEBUG_INVESTIGATE_RE.findall(cot))

    # Fix attempt: look for edit/write verbs in output
    has_fix_attempt = bool(
        re.search(
            r"(edit|write|create|update|fix|modify|patch|change)",
            str(output),
            re.IGNORECASE,
        )
    )

    # Verification: look for test/verify/check verbs
    has_verification = bool(
        re.search(
            r"(test|verify|check|validate|confirm|run)",
            str(output),
            re.IGNORECASE,
        )
    )

    return {
        "self_correction_count": self_correction_count,
        "hypothesis_count": hypothesis_count,
        "investigation_steps": investigation_steps,
        "has_fix_attempt": has_fix_attempt,
        "has_verification": has_verification,
    }


def classify_step_sequence(trace: TraceDict) -> StepSequence:
    """Classify the step sequence from CoT content.

    Splits the CoT text into paragraphs and classifies each.
    Returns the ordered set of unique steps found and their
    transitions.
    """
    cot = trace.get("cot", "")
    if not cot or not cot.strip():
        return StepSequence()

    # Split into paragraphs (potential step boundaries)
    paragraphs = re.split(r"\n\s*\n", cot)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    if not paragraphs:
        return StepSequence()

    # Classify each paragraph
    detected_steps: list[str] = []
    for para in paragraphs:
        step = classify_step(para)
        if step is not None:
            detected_steps.append(step)

    # Deduplicate consecutive same-step
    collapsed: list[str] = []
    for s in detected_steps:
        if not collapsed or collapsed[-1] != s:
            collapsed.append(s)

    steps_tuple = tuple(collapsed)
    transitions = tuple(
        (steps_tuple[i], steps_tuple[i + 1])
        for i in range(len(steps_tuple) - 1)
    )

    return StepSequence(steps=steps_tuple, transitions=transitions)


# ── Aggregation ──────────────────────────────────────────────────


def _build_cot_text(traces: list[TraceDict]) -> str:
    """Build concatenated CoT text from all traces."""
    parts: list[str] = []
    for t in traces:
        cot = t.get("cot", "")
        if cot and cot.strip():
            parts.append(cot)
    return "\n\n".join(parts)


def analyze_behaviors(traces: list[TraceDict]) -> BehaviorStats:
    """Aggregate behavioral signature statistics.

    Args:
        traces: List of parsed trace dicts.

    Returns:
        BehaviorStats with aggregated metrics.
    """
    if not traces:
        return BehaviorStats()

    traces_with_cot = 0
    total_self_corrections = 0
    traces_with_self_correction = 0

    total_hypotheses = 0
    traces_with_hypothesis = 0

    multi_investigation_count = 0

    all_step_counts: Counter[str] = Counter()
    all_transitions: Counter[tuple[str, str]] = Counter()
    total_transitions = 0

    same_turn_fix_count = 0
    traces_with_tools = 0

    for trace in traces:
        cot = trace.get("cot", "")
        has_cot = bool(cot and cot.strip())
        if not has_cot:
            continue

        traces_with_cot += 1

        # Self-correction
        sc_count = detect_self_correction(cot)
        total_self_corrections += sc_count
        if sc_count > 0:
            traces_with_self_correction += 1

        # Hypotheses
        h_count = len(HYPOTHESIS_RE.findall(cot))
        total_hypotheses += h_count
        if h_count > 0:
            traces_with_hypothesis += 1

        # Multi-step investigation detection
        inv_count = len(DEBUG_INVESTIGATE_RE.findall(cot))
        if inv_count >= 3:
            multi_investigation_count += 1

        # Step sequence
        sequence = classify_step_sequence(trace)
        for step in sequence.steps:
            all_step_counts[step] += 1
        for transition in sequence.transitions:
            all_transitions[transition] += 1
            total_transitions += 1

        # Same-turn fix: both fix attempt and verification in same trace
        debug_info = detect_debug_pattern(trace)
        if debug_info["has_fix_attempt"] and debug_info["has_verification"]:
            same_turn_fix_count += 1

    n = max(traces_with_cot, 1)

    # Step coverage rates
    step_coverage = {}
    for step in STEPS:
        step_coverage[step] = round(all_step_counts.get(step, 0) / n, 4)

    # Step transition matrix
    step_transition_matrix: dict[str, dict[str, float]] = {}
    for (from_step, to_step), count in all_transitions.most_common():
        if from_step not in step_transition_matrix:
            step_transition_matrix[from_step] = {}
        step_transition_matrix[from_step][to_step] = (
            round(count / total_transitions, 4) if total_transitions > 0 else 0.0
        )

    return BehaviorStats(
        total_traces=len(traces),
        self_correction_rate=round(
            traces_with_self_correction / n, 4
        ),
        avg_self_corrections=round(total_self_corrections / n, 4),
        hypothesis_driven_rate=round(
            traces_with_hypothesis / n, 4
        ),
        avg_hypotheses=round(total_hypotheses / n, 4),
        multi_investigation_rate=round(
            multi_investigation_count / n, 4
        ),
        step_coverage=step_coverage,
        step_transition_matrix=step_transition_matrix,
        same_turn_fix_rate=round(
            same_turn_fix_count / n, 4
        ),
    )
