"""Tool usage analysis from Fable 5 traces.

Mirrors fable5res DEEP_STATS.json tool_usage section.
Analyzes tool call frequency, type categorization, transition
matrices, read-before-edit rate, and tool-to-text ratio.
"""

import json
import re
import statistics
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List

from analysis.loader import TraceDict

# ── Tool type patterns ───────────────────────────────────────────

TOOL_TYPE_PATTERNS: dict[str, list[str]] = {
    "Bash": ["bash", "terminal", "shell", "sh ", "zsh", "execute"],
    "Read": ["read", "cat ", "view", "show file", "look at"],
    "Edit": ["edit", "write", "create_file", "overwrite", "patch"],
    "Write": ["write", "create_file", "new_file", "save"],
    "Search": ["grep", "search", "find", "glob", "locate"],
    "Glob": ["glob", "ls ", "list_dir", "list directory"],
    "Web": ["fetch", "curl", "wget", "http", "web", "browse"],
    "Think": ["think", "reason", "analyze", "reflect"],
}

TEXT_OUTPUT_TYPES: frozenset[str] = frozenset({"text", "response", "answer"})


@dataclass(frozen=True, slots=True)
class ToolUsageStats:
    """Aggregated tool usage statistics."""

    total_traces: int = 0
    traces_with_tools: int = 0
    tool_calls_per_trace: Dict[str, float] = field(default_factory=dict)
    tool_type_freq: Dict[str, float] = field(default_factory=dict)
    top_tool_calls: List[str] = field(default_factory=list)
    transition_matrix: Dict[str, Dict[str, float]] = field(default_factory=dict)
    read_before_edit_rate: float = 0.0
    verify_after_action_rate: float = 0.0
    tool_to_text_ratio: float = 0.0
    avg_tool_calls: float = 0.0
    max_tool_calls: int = 0


# ── Regex patterns ───────────────────────────────────────────────

TOOL_NAME_RE = re.compile(
    r'(?:"tool_name"|"name"|"tool"|"function")\s*:\s*"([^"]+)"',
    re.IGNORECASE,
)


# ── Per-trace tool parsing ───────────────────────────────────────


def parse_tool_calls(trace: TraceDict) -> list[dict[str, str]]:
    """Extract tool call objects from a trace's output field.

    Handles JSON structured output, lists, and text formats.
    """
    output = trace.get("output", "")
    output_type = trace.get("output_type", "")

    if not output:
        return []

    # JSON object
    if isinstance(output, str) and output.strip().startswith("{"):
        try:
            parsed = json.loads(output)
            return _extract_from_json(parsed)
        except (json.JSONDecodeError, TypeError):
            pass

    # JSON array
    if isinstance(output, list):
        calls: list[dict[str, str]] = []
        for item in output:
            calls.extend(_extract_from_json(item))
        return calls

    # Text-based detection
    if isinstance(output, str):
        return _extract_from_text(output)

    return []


def _extract_from_json(parsed: dict | list) -> list[dict[str, str]]:
    """Extract tool call info from a parsed JSON structure."""
    calls: list[dict[str, str]] = []

    if isinstance(parsed, dict):
        tool_name = (
            parsed.get("name")
            or parsed.get("tool_name")
            or parsed.get("function")
            or parsed.get("tool")
        )
        if tool_name:
            calls.append({"type": _classify_tool(str(tool_name)), "name": str(tool_name)})
        else:
            for key in ("tool_calls", "calls", "functions", "tools", "content"):
                val = parsed.get(key)
                if val and isinstance(val, list):
                    calls.extend(_extract_from_json(val))
    elif isinstance(parsed, list):
        for item in parsed:
            calls.extend(_extract_from_json(item))

    return calls


def _extract_from_text(text: str) -> list[dict[str, str]]:
    """Extract tool call info from a text fragment using regex + keywords."""
    calls: list[dict[str, str]] = []

    names = TOOL_NAME_RE.findall(text)
    for name in names:
        calls.append({"type": _classify_tool(name), "name": name})

    if not calls:
        for tool_type, keywords in TOOL_TYPE_PATTERNS.items():
            for kw in keywords:
                if kw.lower() in text.lower():
                    calls.append({"type": tool_type, "name": kw})
                    break
            if calls:
                break

    return calls


def _classify_tool(name: str) -> str:
    """Classify a tool name into a tool type category."""
    name_lower = name.lower()
    for tool_type, keywords in TOOL_TYPE_PATTERNS.items():
        for keyword in keywords:
            if keyword in name_lower or name_lower in keyword:
                return tool_type
    return "Other"


def is_text_output(trace: TraceDict) -> bool:
    """Check if a trace's output is text (not a tool call)."""
    output_type = trace.get("output_type", "")
    return output_type.lower() in TEXT_OUTPUT_TYPES


def is_verify_action(tool_type: str) -> bool:
    """Check if a tool type is a verification action."""
    verify_keywords = {"Read", "Search", "Glob", "Web"}
    return tool_type in verify_keywords


def is_edit_action(tool_type: str) -> bool:
    """Check if a tool type is an edit/write action."""
    edit_keywords = {"Edit", "Write"}
    return tool_type in edit_keywords


# ── Aggregation ──────────────────────────────────────────────────


def analyze_tool_usage(traces: list[TraceDict]) -> ToolUsageStats:
    """Aggregate tool usage statistics across all traces.

    Args:
        traces: List of parsed trace dicts.

    Returns:
        ToolUsageStats with aggregated metrics.
    """
    if not traces:
        return ToolUsageStats()

    tool_call_counts: list[int] = []
    type_counts: Counter[str] = Counter()
    all_tool_names: Counter[str] = Counter()

    all_transitions: Counter[tuple[str, str]] = Counter()
    total_transitions = 0

    read_before_edit_count = 0
    total_edit_sequences = 0

    verify_after_action_count = 0
    total_action_sequences = 0

    tool_output_count = 0
    text_output_count = 0

    traces_with_tools = 0

    for trace in traces:
        calls = parse_tool_calls(trace)
        n_calls = len(calls)

        if n_calls > 0:
            traces_with_tools += 1
        tool_call_counts.append(n_calls)

        for call in calls:
            type_counts[call["type"]] += 1
            all_tool_names[call["name"]] += 1

        # Transition matrix
        types = [c["type"] for c in calls]
        for i in range(len(types) - 1):
            all_transitions[(types[i], types[i + 1])] += 1
            total_transitions += 1

        # Read-before-edit
        for i in range(1, len(types)):
            if is_edit_action(types[i]):
                total_edit_sequences += 1
                if is_verify_action(types[i - 1]):
                    read_before_edit_count += 1

        # Verify-after-action
        for i in range(1, len(types)):
            if not is_verify_action(types[i - 1]) and is_verify_action(types[i]):
                verify_after_action_count += 1
                total_action_sequences += 1

        # Tool-to-text
        if is_text_output(trace):
            text_output_count += 1
        elif n_calls > 0:
            tool_output_count += 1

    n = len(traces)
    avg_tool_calls = statistics.mean(tool_call_counts) if tool_call_counts else 0.0
    max_tool_calls = max(tool_call_counts) if tool_call_counts else 0

    total_calls = sum(type_counts.values()) or 1
    tool_type_freq = {
        tool_type: round(count / n, 4)
        for tool_type, count in type_counts.most_common()
    }

    tool_calls_per_trace = _distribution(tool_call_counts)

    transition_matrix: dict[str, dict[str, float]] = {}
    for (from_type, to_type), count in all_transitions.most_common():
        if from_type not in transition_matrix:
            transition_matrix[from_type] = {}
        transition_matrix[from_type][to_type] = (
            round(count / total_transitions, 4) if total_transitions > 0 else 0.0
        )

    return ToolUsageStats(
        total_traces=n,
        traces_with_tools=traces_with_tools,
        tool_calls_per_trace=tool_calls_per_trace,
        tool_type_freq=tool_type_freq,
        top_tool_calls=[name for name, _ in all_tool_names.most_common(15)],
        transition_matrix=transition_matrix,
        read_before_edit_rate=round(
            read_before_edit_count / total_edit_sequences, 4
        )
        if total_edit_sequences > 0
        else 0.0,
        verify_after_action_rate=round(
            verify_after_action_count / total_action_sequences, 4
        )
        if total_action_sequences > 0
        else 0.0,
        tool_to_text_ratio=round(
            tool_output_count / (tool_output_count + text_output_count), 4
        )
        if (tool_output_count + text_output_count) > 0
        else 0.0,
        avg_tool_calls=round(avg_tool_calls, 2),
        max_tool_calls=max_tool_calls,
    )


def _distribution(counts: list[int]) -> dict[str, float]:
    """Build a distribution map from value counts."""
    if not counts:
        return {}
    counter = Counter(counts)
    n = len(counts)
    return {str(k): round(v / n, 4) for k, v in sorted(counter.items())}
