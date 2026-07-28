"""Enhance SKILL.md files with extracted pattern data from analysis pipeline.
Takes pattern YAML files and merges new stats into the existing skill files."""
import json
import re
from pathlib import Path
from typing import Any

import yaml

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_SKILLS_DIR = _PROJECT_ROOT / "skills"
_PATTERNS_DIR = _PROJECT_ROOT / "analysis" / "patterns"
_STATS_PATH = _PATTERNS_DIR / "combined_stats.json"

SKILL_MAP = {
    "think": "deepseek-think",
    "code": "deepseek-code",
    "debug": "deepseek-debug",
    "architect": "deepseek-architect",
    "verify": "deepseek-verify",
}


def load_patterns() -> dict[str, dict[str, Any]]:
    patterns: dict[str, dict[str, Any]] = {}
    for skill_key in SKILL_MAP:
        path = _PATTERNS_DIR / f"{skill_key}_patterns.yaml"
        if path.exists():
            with open(path) as f:
                data = yaml.safe_load(f)
                patterns[skill_key] = data
    return patterns


def load_combined_stats() -> dict[str, Any] | None:
    if _STATS_PATH.exists():
        return json.loads(_STATS_PATH.read_text())
    return None


def _fmt(val: Any, fmt: str) -> str:
    if isinstance(val, dict | list):
        return str(val)
    if isinstance(val, float):
        return f"{val:{fmt}}"
    return str(val)


def build_stats_block(cot: dict[str, Any], tools: dict[str, Any], behaviors: dict[str, Any], total: int) -> str:
    tcpt = tools.get("tool_calls_per_trace", 0)
    tcpt_str = _fmt(tcpt, ".2f")

    lines = [
        f"## Quantitative Facts (from {total} trace analysis)",
        "",
        "### CoT Structure",
        f"- CoT Rate: {_fmt(cot.get('cot_rate', 0), '.1%')}",
        f"- Avg Tokens: {_fmt(cot.get('avg_tokens', 0), '.1f')}",
        f"- Avg Paragraphs: {_fmt(cot.get('avg_paragraphs', 0), '.1f')}",
        f"- Avg Sentences: {_fmt(cot.get('avg_sentences', 0), '.1f')}",
        f"- Self-Correction Rate: {_fmt(behaviors.get('self_correction_rate', 0), '.1%')}",
        f"- Avg Self-Corrections: {_fmt(behaviors.get('avg_self_corrections', 0), '.2f')}",
        f"- Reasoning Connectors/Turn: {_fmt(cot.get('reasoning_connectors_per_turn', 0), '.2f')}",
        "",
        "### Behavioral",
        f"- Hypothesis-Driven Rate: {_fmt(behaviors.get('hypothesis_driven_rate', 0), '.1%')}",
        f"- Multi-Investigation Rate: {_fmt(behaviors.get('multi_investigation_rate', 0), '.1%')}",
        f"- Same-Turn Fix Rate: {_fmt(behaviors.get('same_turn_fix_rate', 0), '.1%')}",
        "",
        "### Tool Usage",
        f"- Tool Calls/Trace: {tcpt_str}",
        f"- Avg Tool Calls: {_fmt(tools.get('avg_tool_calls', 0), '.1f')}",
        f"- Read-Before-Edit Rate: {_fmt(tools.get('read_before_edit_rate', 0), '.1%')}",
        f"- Verify-After-Action Rate: {_fmt(tools.get('verify_after_action_rate', 0), '.1%')}",
        f"- Tool-to-Text Ratio: {_fmt(tools.get('tool_to_text_ratio', 0), '.2f')}",
        "",
    ]
    return "\n".join(lines)


def build_patterns_block(patterns: list[dict[str, Any]], anti_patterns: list[dict[str, Any]]) -> str:
    lines = ["### Extracted Behavioral Patterns", ""]
    for p in patterns:
        name = p.get("name", "unknown")
        desc = p.get("description", "")
        freq = p.get("frequency", 0)
        if isinstance(freq, float):
            lines.append(f"- **{name}** ({freq:.1%}): {desc}")
        else:
            lines.append(f"- **{name}** ({freq}): {desc}")
    if anti_patterns:
        lines.extend(["", "### Anti-Patterns to Avoid", ""])
        for ap in anti_patterns:
            name = ap.get("name", "unknown")
            desc = ap.get("description", "")
            freq = ap.get("frequency", 0)
            if isinstance(freq, float):
                lines.append(f"- **{name}** ({freq:.1%}): {desc}")
            else:
                lines.append(f"- **{name}** ({freq}): {desc}")
    return "\n".join(lines)


def enhance_skill(skill_key: str, existing_skill: str, pattern_data: dict[str, Any]) -> str:
    stats = pattern_data.get("stats", {})
    cot = stats.get("cot", {})
    tools = stats.get("tool_usage", {})
    behaviors = stats.get("behaviors", {})
    patterns = pattern_data.get("patterns", [])
    anti_patterns = pattern_data.get("anti_patterns", [])
    total_traces = pattern_data.get("total_traces", 0)

    stats_block = build_stats_block(cot, tools, behaviors, total_traces)
    patterns_block = build_patterns_block(patterns, anti_patterns)

    enhancement = f"""
---

## Enhanced Pattern Data (from {total_traces} traces)

{stats_block}

{patterns_block}

---

""".lstrip()

    # Insert the enhancement block before the last "---" or at the end
    if existing_skill.strip().endswith("---"):
        insert_pos = existing_skill.rstrip().rfind("---")
        if insert_pos >= 0:
            before = existing_skill[:insert_pos].rstrip()
            after = existing_skill[insert_pos:]
            return f"{before}\n\n{enhancement}{after}"
    return f"{existing_skill.rstrip()}\n\n{enhancement}"


def main() -> None:
    patterns = load_patterns()
    stats = load_combined_stats()

    if stats:
        total = stats.get("total_traces", 0)
        print(f"Loaded combined stats: {total} traces analyzed")
        print(f"Skill distribution: {stats.get('skill_distribution', {})}")
    else:
        print("No combined stats found")

    for skill_key, skill_dir_name in SKILL_MAP.items():
        skill_path = _SKILLS_DIR / skill_dir_name / "SKILL.md"
        if not skill_path.exists():
            print(f"  SKIP {skill_dir_name}: no existing SKILL.md")
            continue

        pattern_data = patterns.get(skill_key)
        if not pattern_data or pattern_data.get("total_traces", 0) == 0:
            print(f"  SKIP {skill_dir_name}: no pattern data ({pattern_data})")
            continue

        existing = skill_path.read_text()
        enhanced = enhance_skill(skill_key, existing, pattern_data)

        out_path = _SKILLS_DIR / skill_dir_name / "SKILL.enhanced.md"
        out_path.write_text(enhanced)
        print(f"  ✓ {skill_dir_name}: {pattern_data['total_traces']} traces -> {out_path.name}")


if __name__ == "__main__":
    main()
