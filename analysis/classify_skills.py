"""Skill category classification for Fable 5 traces.

Assigns each trace to one of 5 skill axes based on keyword/pattern
matching on CoT and output content.
"""

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from analysis.loader import TraceDict

# ── Skill categories ─────────────────────────────────────────────

SKILL_CATEGORIES: list[str] = [
    "think",
    "code",
    "debug",
    "architect",
    "verify",
]


@dataclass(frozen=True, slots=True)
class SkillClassification:
    """Classification result for a single trace."""

    skill: str
    confidence: float
    scores: Dict[str, float]


@dataclass(frozen=True, slots=True)
class SkillStats:
    """Aggregated skill distribution stats."""

    total_traces: int = 0
    distribution: Dict[str, float] = field(default_factory=dict)
    distribution_counts: Dict[str, int] = field(default_factory=dict)
    avg_confidence: Dict[str, float] = field(default_factory=dict)


# ── Keyword definitions ──────────────────────────────────────────


# (pattern, weight) tuples per skill
SKILL_KEYWORDS: dict[str, list[tuple[str, int]]] = {
    "think": [
        (r"\bthink\b", 3),
        (r"\breason\b", 3),
        (r"\banalyze\b", 2),
        (r"\bunderstand\b", 2),
        (r"\bconsider\b", 2),
        (r"\bponder\b", 2),
        (r"\breflect\b", 2),
        (r"\bcontemplate\b", 2),
        (r"\bdelve\b", 1),
        (r"\bexamine\b", 1),
        (r"\bweigh\b", 1),
        (r"\breasoning\b", 3),
        (r"\bthought\b", 2),
        (r"\bcognitive\b", 1),
        (r"\bmental model\b", 2),
        (r"\bhypothesize\b", 2),
        (r"\btheorize\b", 2),
        (r"\bdeduce\b", 2),
        (r"\binfer\b", 2),
        (r"\bconclude\b", 1),
    ],
    "code": [
        (r"\bimplement\b", 3),
        (r"\bfunction\b", 2),
        (r"\bclass\b", 2),
        (r"\bvariable\b", 2),
        (r"\bimport\b", 2),
        (r"\bdef\b", 3),
        (r"\breturn\b", 2),
        (r"\bargument\b", 1),
        (r"\bparameter\b", 1),
        (r"\bcall\b", 1),
        (r"\bcode\b", 2),
        (r"\bwrite\b", 2),
        (r"\bcreate\b", 2),
        (r"\badd\b", 1),
        (r"\bmodule\b", 1),
        (r"\bpackage\b", 1),
        (r"\bcompile\b", 1),
        (r"\bsyntax\b", 2),
        (r"\balgorithm\b", 2),
        (r"\btype\b", 1),
        (r"\bapi\b", 1),
        (r"\blibrary\b", 1),
        (r"\bframework\b", 1),
    ],
    "debug": [
        (r"\bbug\b", 3),
        (r"\berror\b", 3),
        (r"\bfix\b", 3),
        (r"\bissue\b", 2),
        (r"\bproblem\b", 2),
        (r"\bfail\b", 3),
        (r"\bcrash\b", 2),
        (r"\bexception\b", 2),
        (r"\bstack trace\b", 3),
        (r"\btraceback\b", 3),
        (r"\broot cause\b", 3),
        (r"\breproduce\b", 2),
        (r"\bdebug\b", 3),
        (r"\bincorrect\b", 2),
        (r"\bwrong\b", 2),
        (r"\bbroken\b", 2),
        (r"\bnot working\b", 2),
        (r"\bunexpected\b", 2),
        (r"\btroubleshoot\b", 2),
        (r"\bdiagnose\b", 2),
        (r"\binvestigate\b", 2),
        (r"\bregression\b", 2),
        (r"\bactually\b", 1),
        (r"\bwait\b", 1),
    ],
    "architect": [
        (r"\bdesign\b", 3),
        (r"\barchitecture\b", 3),
        (r"\bpattern\b", 2),
        (r"\bcomponent\b", 2),
        (r"\bmodule\b", 2),
        (r"\bsystem\b", 2),
        (r"\binterface\b", 2),
        (r"\babstract\b", 2),
        (r"\bplan\b", 2),
        (r"\bapproach\b", 2),
        (r"\bstrategy\b", 2),
        (r"\bdiagram\b", 1),
        (r"\bflow\b", 1),
        (r"\bdata flow\b", 2),
        (r"\bdecompos\b", 2),
        (r"\brefactor\b", 2),
        (r"\bscalab\b", 2),
        (r"\bmaintainab\b", 2),
        (r"\bextensib\b", 2),
        (r"\bcoupling\b", 2),
        (r"\bcohesion\b", 2),
        (r"\bmodel-view\b", 2),
        (r"\bmicroservice\b", 2),
        (r"\bdependency\b", 2),
        (r"\bseparation of concerns\b", 3),
    ],
    "verify": [
        (r"\btest\b", 3),
        (r"\bassert\b", 3),
        (r"\bverify\b", 3),
        (r"\bvalidate\b", 3),
        (r"\bcheck\b", 2),
        (r"\bconfirm\b", 2),
        (r"\bensure\b", 2),
        (r"\bunit test\b", 3),
        (r"\bintegration test\b", 3),
        (r"\be2e\b", 2),
        (r"\bassertion\b", 2),
        (r"\bcoverage\b", 2),
        (r"\bquality\b", 1),
        (r"\breview\b", 1),
        (r"\baudit\b", 1),
        (r"\blint\b", 1),
        (r"\bstatic analysis\b", 2),
        (r"\bproof\b", 1),
        (r"\bmock\b", 1),
        (r"\bfixture\b", 1),
        (r"\banonymous\b", 0),  # neutral
    ],
}


# ── Classification ───────────────────────────────────────────────


def get_skill_keywords() -> Dict[str, List[str]]:
    """Return the keyword lists for all skill categories (for inspection)."""
    return {
        skill: [kw for kw, _ in kws]
        for skill, kws in SKILL_KEYWORDS.items()
    }


def classify_trace_skill(trace: TraceDict) -> SkillClassification:
    """Classify a single trace into a skill category.

    Scoring is based on keyword density in CoT + output text.
    Returns the winning skill with confidence score.
    """
    cot = trace.get("cot", "")
    output = trace.get("output", "")
    context = trace.get("context", "")

    # Combine text sources
    text_parts: list[str] = []
    if isinstance(cot, str) and cot.strip():
        text_parts.append(cot)
    if isinstance(output, str) and output.strip():
        text_parts.append(output)
    if isinstance(context, str) and context.strip():
        text_parts.append(context)

    combined = " ".join(text_parts)
    if not combined.strip():
        return SkillClassification(skill="think", confidence=0.0, scores={})

    combined_lower = combined.lower()

    # Score each skill
    raw_scores: dict[str, int] = {}
    for skill, patterns in SKILL_KEYWORDS.items():
        score = 0
        for pattern, weight in patterns:
            matches = re.findall(pattern, combined_lower)
            if matches:
                score += weight * len(matches)
        raw_scores[skill] = score

    # Normalize to confidence (0-1 range)
    total_score = sum(raw_scores.values()) or 1
    scores: dict[str, float] = {
        skill: round(score / total_score, 4)
        for skill, score in raw_scores.items()
    }

    # Find winner
    winner = max(raw_scores, key=raw_scores.get)  # type: ignore[arg-type]
    winner_score = max(raw_scores.values())
    confidence = round(winner_score / total_score, 4) if total_score > 0 else 0.0

    return SkillClassification(
        skill=winner,
        confidence=confidence,
        scores=scores,
    )


# ── Aggregation ──────────────────────────────────────────────────


def aggregate_skill_stats(
    classifications: list[SkillClassification],
) -> SkillStats:
    """Aggregate classification results across traces.

    Args:
        classifications: List of per-trace classification results.

    Returns:
        SkillStats with distribution and average confidence.
    """
    if not classifications:
        return SkillStats()

    n = len(classifications)
    counter: Counter[str] = Counter()
    confidence_sums: dict[str, float] = {}
    confidence_counts: dict[str, int] = {}

    for cls in classifications:
        counter[cls.skill] += 1
        if cls.skill not in confidence_sums:
            confidence_sums[cls.skill] = 0.0
            confidence_counts[cls.skill] = 0
        confidence_sums[cls.skill] += cls.confidence
        confidence_counts[cls.skill] += 1

    distribution = {skill: round(count / n, 4) for skill, count in counter.most_common()}
    distribution_counts = dict(counter.most_common())
    avg_confidence = {
        skill: round(confidence_sums[skill] / confidence_counts[skill], 4)
        for skill in confidence_sums
    }

    # Ensure all 5 skills appear in distribution (even if 0)
    for skill in SKILL_CATEGORIES:
        if skill not in distribution:
            distribution[skill] = 0.0
            distribution_counts[skill] = 0
            avg_confidence[skill] = 0.0

    return SkillStats(
        total_traces=n,
        distribution=distribution,
        distribution_counts=distribution_counts,
        avg_confidence=avg_confidence,
    )
