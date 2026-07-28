"""Chain-of-thought structure analysis.

Mirrors fable5res DEEP_STATS.json cot_stats section.
Analyzes per-trace CoT structure: length, opener words, pronoun
distribution, self-correction markers, reasoning connectors.
"""

import re
import statistics
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from analysis.loader import TraceDict

# Convenience re-exports for user-facing API
# (mirrors the function names from the spec)


def count_opener_words(cot: str) -> dict[str, int]:
    """Count opener word occurrences in CoT text (convenience wrapper)."""
    metrics = analyze_single_cot(cot)
    if metrics.opener_word:
        return {metrics.opener_word: 1}
    return {}


def find_self_corrections(cot: str) -> list[str]:
    """Find self-correction markers in CoT text (convenience wrapper)."""
    import re  # noqa: PLC0415

    markers = [
        "actually",
        "however",
        "wait",
        "no",
        "instead",
        "rather",
        "let me reconsider",
        "on second thought",
        "hold on",
        "that's not right",
        "that is not right",
        "i made a mistake",
        "i was wrong",
        "let me think again",
        "rethinking",
    ]
    cot_lower = cot.lower()
    found: list[str] = []
    for marker in markers:
        if marker in cot_lower:
            found.append(marker)
    return found

# ── Word lists ───────────────────────────────────────────────────

OPENER_WORDS: list[str] = [
    "Alright",
    "Okay",
    "Let me",
    "So",
    "First",
    "I need to",
    "I'll",
    "The",
    "We",
    "This",
]

PRONOUN_FIRST: list[str] = ["I", "me", "my", "mine", "we", "us", "our"]
PRONOUN_SECOND: list[str] = ["you", "your", "yours"]
PRONOUN_THIRD: list[str] = [
    "he",
    "she",
    "it",
    "they",
    "them",
    "their",
    "his",
    "her",
    "its",
]

SELF_CORRECTION_MARKERS: list[str] = [
    "actually",
    "however",
    "wait",
    "no",
    "instead",
    "rather",
    "let me reconsider",
    "on second thought",
    "hold on",
    "that's not right",
    "that is not right",
    "i made a mistake",
    "i was wrong",
    "let me think again",
    "rethinking",
]

REASONING_CONNECTORS: list[str] = [
    "because",
    "since",
    "therefore",
    "thus",
    "hence",
    "consequently",
    "accordingly",
    "as a result",
    "this means",
    "which implies",
    "given that",
    "so then",
]

# ── Regex patterns ───────────────────────────────────────────────

# Split on sentence-ending punctuation (preserving acronyms like "e.g.")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'(])")
_PARAGRAPH_SPLIT_RE = re.compile(r"\n\s*\n")


# ── Dataclasses ──────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class CotStats:
    """Aggregated CoT statistics for a skill category."""

    total_traces: int = 0
    cot_present: int = 0
    cot_rate: float = 0.0
    avg_words: float = 0.0
    avg_chars: float = 0.0
    avg_paragraphs: float = 0.0
    avg_sentences: float = 0.0
    median_words: float = 0.0
    max_words: int = 0
    min_words: int = 0
    opener_word_freq: Dict[str, float] = field(default_factory=dict)
    pronoun_first_pct: float = 0.0
    pronoun_second_pct: float = 0.0
    pronoun_third_pct: float = 0.0
    self_correction_rate: float = 0.0
    avg_self_corrections: float = 0.0
    avg_reasoning_connectors: float = 0.0
    top_connectors: List[str] = field(default_factory=list)


@dataclass(slots=True)  # noqa: MUTABLE_OK — running accumulator, not a value object
class TraceCotMetrics:
    """Per-trace CoT metrics (mutable accumulator)."""

    word_count: int = 0
    char_count: int = 0
    paragraph_count: int = 0
    sentence_count: int = 0
    opener_word: str = ""
    pronoun_first: int = 0
    pronoun_second: int = 0
    pronoun_third: int = 0
    self_correction_count: int = 0
    reasoning_connector_count: int = 0
    connector_counter: Counter[str] = field(default_factory=Counter)


# ── Per-trace analysis ───────────────────────────────────────────


def analyze_single_cot(cot: str) -> TraceCotMetrics:
    """Compute CoT metrics for a single trace."""
    metrics = TraceCotMetrics()

    # Strip <think> tags if present
    cot_clean = _strip_think_tags(cot)

    metrics.char_count = len(cot_clean)
    metrics.word_count = len(cot_clean.split()) if cot_clean.strip() else 0

    # Paragraphs
    paragraphs = [p.strip() for p in _PARAGRAPH_SPLIT_RE.split(cot_clean) if p.strip()]
    metrics.paragraph_count = len(paragraphs) if paragraphs else (1 if cot_clean.strip() else 0)

    # Sentences
    sentences = _SENTENCE_SPLIT_RE.split(cot_clean)
    sentences = [s.strip() for s in sentences if s.strip()]
    metrics.sentence_count = len(sentences) if sentences else 0

    # Opener word
    first_word = _get_first_word(cot_clean)
    metrics.opener_word = _match_opener(first_word, sentences)

    # Pronouns
    words_lower = cot_clean.lower().split()
    metrics.pronoun_first = sum(1 for w in words_lower if w in PRONOUN_FIRST)
    metrics.pronoun_second = sum(1 for w in words_lower if w in PRONOUN_SECOND)
    metrics.pronoun_third = sum(1 for w in words_lower if w in PRONOUN_THIRD)

    # Self-correction markers
    cot_lower = cot_clean.lower()
    metrics.self_correction_count = _count_markers(cot_lower, SELF_CORRECTION_MARKERS)

    # Reasoning connectors
    connector_count = 0
    for marker in REASONING_CONNECTORS:
        count = cot_lower.count(marker)
        if count > 0:
            metrics.connector_counter[marker] += count
            connector_count += count
    metrics.reasoning_connector_count = connector_count

    return metrics


def _strip_think_tags(text: str) -> str:
    """Remove <think>...</think> tags and their content if present."""
    stripped = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return stripped.strip()


def _get_first_word(text: str) -> str:
    """Return the first word of text (lowercased)."""
    words = text.strip().split()
    if not words:
        return ""
    return words[0].lower()


def _match_opener(first_word: str, sentences: list[str]) -> str:
    """Match the first utterance against known opener patterns."""
    first_sentence = sentences[0].strip() if sentences else first_word
    first_lower = first_sentence.lower()

    for opener in OPENER_WORDS:
        opener_lower = opener.lower()
        if first_lower.startswith(opener_lower):
            return opener
        # Also check just the first word
        if first_word == opener_lower:
            return opener

    return first_word.capitalize() if first_word else ""


def _count_markers(text_lower: str, markers: list[str]) -> int:
    """Count occurrences of markers in lowercased text."""
    total = 0
    for marker in markers:
        total += text_lower.count(marker)
    return total


# ── Aggregation ──────────────────────────────────────────────────


def analyze_cot_structure(traces: list[TraceDict]) -> CotStats:
    """Aggregate CoT metrics across all traces in a sample.

    Args:
        traces: List of parsed trace dicts (must have 'cot' field).

    Returns:
        CotStats with aggregated metrics.
    """
    if not traces:
        return CotStats()

    all_metrics: list[TraceCotMetrics] = []
    all_opener_freq: Counter[str] = Counter()
    all_connectors: Counter[str] = Counter()
    cot_present = 0
    total_words: list[int] = []

    for trace in traces:
        cot = trace.get("cot", "")
        has_cot = bool(cot and cot.strip())

        if has_cot:
            metrics = analyze_single_cot(cot)
            all_metrics.append(metrics)
            all_opener_freq[metrics.opener_word] += 1
            all_connectors += metrics.connector_counter
            total_words.append(metrics.word_count)
            cot_present += 1

    n = len(all_metrics)
    if n == 0:
        return CotStats(total_traces=len(traces))

    # Word stats
    avg_words = statistics.mean(total_words) if total_words else 0.0
    median_words = statistics.median(total_words) if total_words else 0.0

    # Opener word frequencies (as percentages)
    total_traces_with_cot = n
    opener_freq: dict[str, float] = {}
    for word, count in all_opener_freq.most_common(10):
        opener_freq[word] = round(count / total_traces_with_cot, 4)

    # Pronoun distribution
    total_pronouns = sum(
        m.pronoun_first + m.pronoun_second + m.pronoun_third for m in all_metrics
    )
    if total_pronouns > 0:
        first_pct = sum(m.pronoun_first for m in all_metrics) / total_pronouns
        second_pct = sum(m.pronoun_second for m in all_metrics) / total_pronouns
        third_pct = sum(m.pronoun_third for m in all_metrics) / total_pronouns
    else:
        first_pct = second_pct = third_pct = 0.0

    # Self-correction
    total_corrections = sum(m.self_correction_count for m in all_metrics)
    traces_with_correction = sum(
        1 for m in all_metrics if m.self_correction_count > 0
    )

    # Reasoning connectors
    total_connectors = sum(m.reasoning_connector_count for m in all_metrics)

    # Averages
    avg_paragraphs = statistics.mean(m.paragraph_count for m in all_metrics)
    avg_sentences = statistics.mean(m.sentence_count for m in all_metrics)
    avg_chars = statistics.mean(m.char_count for m in all_metrics)

    return CotStats(
        total_traces=len(traces),
        cot_present=cot_present,
        cot_rate=round(cot_present / len(traces), 4),
        avg_words=round(avg_words, 2),
        avg_chars=round(avg_chars, 2),
        avg_paragraphs=round(avg_paragraphs, 2),
        avg_sentences=round(avg_sentences, 2),
        median_words=round(median_words, 2),
        max_words=max(total_words) if total_words else 0,
        min_words=min(total_words) if total_words else 0,
        opener_word_freq=opener_freq,
        pronoun_first_pct=round(first_pct, 4),
        pronoun_second_pct=round(second_pct, 4),
        pronoun_third_pct=round(third_pct, 4),
        self_correction_rate=round(
            traces_with_correction / total_traces_with_cot, 4
        )
        if total_traces_with_cot > 0
        else 0.0,
        avg_self_corrections=round(
            total_corrections / total_traces_with_cot, 4
        )
        if total_traces_with_cot > 0
        else 0.0,
        avg_reasoning_connectors=round(
            total_connectors / total_traces_with_cot, 4
        )
        if total_traces_with_cot > 0
        else 0.0,
        top_connectors=[
            w for w, _ in all_connectors.most_common(5)
        ],
    )
