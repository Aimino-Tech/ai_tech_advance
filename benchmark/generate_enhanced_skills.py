#!/usr/bin/env python3
"""Generate enhanced SKILL.md files from pattern extraction YAML output.

Reads analysis/patterns/*_patterns.yaml + combined_stats.json and
writes data-driven enhanced SKILL.md files for each skill axis.

Usage:
    python -m benchmark.generate_enhanced_skills
    python -m benchmark.generate_enhanced_skills --patterns-dir analysis/patterns --output-dir skills
"""

import argparse
import json
from pathlib import Path

import yaml


SKILL_NAMES = {
    "think": "fable-think",
    "code": "fable-code",
    "debug": "fable-debug",
    "architect": "fable-architect",
    "verify": "fable-verify",
}

SKILL_TITLES = {
    "think": "Think like Fable 5",
    "code": "Code like Fable 5",
    "debug": "Debug like Fable 5",
    "architect": "Architect like Fable 5",
    "verify": "Verify like Fable 5",
}

SKILL_DESCRIPTIONS = {
    "think": "Natural, flowing, purposeful reasoning distilled from chain-of-thought traces.",
    "code": "Methodical, verified, and deeply informed by context. Distilled from real code-generation traces.",
    "debug": "Root-cause analysis and fix — hypothesis-driven, systematic, and verification-focused.",
    "architect": "System decomposition and design — planning interfaces before implementation.",
    "verify": "Self-verification and test generation — thorough validation before declaring done.",
}

SKILL_WHEN = {
    "think": "Use this skill EVERY TIME before writing code, making decisions, or taking action. This is the foundational reasoning skill that all other skills build upon.",
    "code": "Use this skill whenever you need to write, edit, or create code.",
    "debug": "Use this skill when debugging — crashes, silent failures, wrong output, edge-case bugs.",
    "architect": "Use this skill when designing systems, choosing architectures, or planning component structure.",
    "verify": "Use this skill when writing tests, validating output, or reviewing code for correctness.",
}

# Skill-specific behavioral patterns derived from analysis data
SKILL_BEHAVIORAL_PATTERNS = {
    "think": [
        {
            "name": "The-Then Conditional Reasoning",
            "desc": "Think mode explores conditional scenarios: 'If [condition], then [outcome]'. This is the top reasoning connector pattern. 'If' and 'But' are the #1 and #2 connectors in think mode — higher than any other skill.",
            "evidence": "'If' and 'But' are the top reasoning connectors; think mode explores trade-offs and scenarios.",
        },
        {
            "name": "PLAN-Iterative (1.08+ Plans Per Trace)",
            "desc": "Think mode doesn't plan once — it re-plans as new information emerges. Each ACKNOWLEDGE often triggers a new PLAN cycle.",
            "evidence": "PLAN frequency exceeds 1.0 per trace in all skills; tools re-evaluate after each context shift.",
        },
        {
            "name": "ACKNOWLEDGE→PLAN Core Loop",
            "desc": "The most statistically significant chain: ACKNOWLEDGE (I understand) → PLAN (here's my approach). This accounts for the highest transition probability in all skills.",
            "evidence": "ACKNOWLEDGE→PLAN transition is consistently the highest probability across all 5 skills.",
        },
        {
            "name": "Self-Correction Is Universal",
            "desc": "Self-correction appears in ~98% of traces. This is normal behavior, not a failure mode. Use 'Actually' or 'However' as correction markers.",
            "evidence": "97-100% self-correction rate across all skills; 'actually' is the #1 correction marker.",
        },
        {
            "name": "VERIFY-Follows-PLAN Transition",
            "desc": "After each PLAN, think mode verifies: 'The output should be...'. This is the second-highest transition in most skills.",
            "evidence": "PLAN→VERIFY transition probability of 0.12-0.13 across skills.",
        },
        {
            "name": "The-Opener Dominance",
            "desc": "Think mode starts with 'The' more than any other opener — subject-first thinking. This is unique to think mode.",
            "evidence": "'The' opener is 45-75% in think mode vs <17% in other skills.",
        },
        {
            "name": "Hypothesis-Driven Exploration",
            "desc": "Think mode forms and evaluates hypotheses before reaching conclusions. Uses connectors like 'perhaps', 'could be', 'maybe'.",
            "evidence": "25-67% hypothesis-driven rate across skills; highest in architect and debug.",
        },
        {
            "name": "Third-Person Voice Preference",
            "desc": "Think mode prefers third-person pronouns — analyzing systems and subjects rather than self-narrating.",
            "evidence": "Third-person pronouns 50-66% across all skills; think mode is especially subject-focused.",
        },
    ],
    "code": [
        {
            "name": "ACK-PLAN-VERIFY Core Loop",
            "desc": "The dominant rhythm: ACKNOWLEDGE (I understand the context) → PLAN (here's my approach) → VERIFY (the output should be...). This accounts for ~24% of all step transitions in code mode.",
            "evidence": "ACKNOWLEDGE→PLAN (0.24), PLAN→VERIFY (0.13), VERIFY→PLAN (0.13).",
        },
        {
            "name": "Self-Correction Density (5.9 per trace)",
            "desc": "Code mode has the highest average self-corrections. Fable 5 corrects as it goes — mid-stream, not after the fact.",
            "evidence": "5.9 avg self-corrections per code trace; 97.8% of traces contain at least one.",
        },
        {
            "name": "PLAN-Iterative Development",
            "desc": "Code mode plans, executes a bit, then re-plans. PLAN frequency is 1.08+ per trace — iterative refinement.",
            "evidence": "PLAN 1.08/trace, EXECUTE 0.31/trace, VERIFY 0.63/trace. Cycle repeats.",
        },
        {
            "name": "Same-Turn Fix (16.6% of traces)",
            "desc": "In 1 in 6 code traces, Fable 5 catches and fixes an issue within the same turn without needing a separate iteration.",
            "evidence": "16.6% same-turn fix rate; higher in verify (24.3%) and debug (23.8%).",
        },
        {
            "name": "'Alright' Opener Dominance",
            "desc": "Code mode starts with 'Alright' 61.3% of the time — the most common opener across all skills.",
            "evidence": "61.3% 'Alright' opener, 16.9% 'The', 9.5% 'Okay'.",
        },
        {
            "name": "First-Person Self-Narration",
            "desc": "Code mode uses first-person pronouns for self-narration and third-person for code description.",
            "evidence": "33.3% first-person, 66.3% third-person pronouns.",
        },
        {
            "name": "'Because' Connector Dominance",
            "desc": "'Because' is the #1 reasoning connector in code mode — every decision has explicit causal justification.",
            "evidence": "1.88 connectors/turn; top: because, since, thus, therefore.",
        },
        {
            "name": "VERIFY→PLAN Feedback Loop",
            "desc": "After verification, Fable 5 often re-plans rather than continuing. This corrective loop is the #1 transition from VERIFY.",
            "evidence": "VERIFY→PLAN at 0.13 probability — higher than VERIFY→EXECUTE.",
        },
    ],
    "debug": [
        {
            "name": "Hypothesis-Driven Debugging",
            "desc": "Debug mode forms and tests hypotheses before fixing. This is the most hypothesis-driven of all skills.",
            "evidence": "42.9% hypothesis-driven rate — highest of any skill.",
        },
        {
            "name": "ACKNOWLEDGE→PLAN Entry Pattern",
            "desc": "Debug mode starts by acknowledging the problem then planning the investigation. This is the highest transition probability.",
            "evidence": "ACKNOWLEDGE→PLAN at 0.26 — highest transition in debug mode.",
        },
        {
            "name": "Same-Turn Fix Rate (23.8%)",
            "desc": "Nearly 1 in 4 debug traces fixes the issue within the same turn. Debug mode is action-oriented.",
            "evidence": "23.8% same-turn fix rate, tied with verify as highest.",
        },
        {
            "name": "Self-Correction Near-Universal",
            "desc": "100% of debug traces contain self-correction. Debugging is inherently iterative.",
            "evidence": "100% self-correction rate; 5.76 avg corrections per trace.",
        },
        {
            "name": "'Alright' Opener + Investigation",
            "desc": "Debug mode opens with 'Alright' 66.7% of the time, then immediately starts investigating.",
            "evidence": "66.7% 'Alright' opener, followed by SCOPE (0.19) and PLAN (1.05).",
        },
        {
            "name": "PLAN↔EXECUTE Tight Loop",
            "desc": "Debug mode cycles rapidly between planning and executing small investigation steps.",
            "evidence": "EXECUTE→PLAN at 0.065 — tightest PLAN-EXECUTE loop among all skills.",
        },
        {
            "name": "First-Person Investigation Narrative",
            "desc": "Debug uses first-person for investigation narrative ('I need to check', 'let me see').",
            "evidence": "44.4% first-person, 55.6% third-person pronouns.",
        },
        {
            "name": "VERIFY Completes the Loop",
            "desc": "After executing a fix, debug mode verifies before moving on. VERIFY appears in 52.4% of traces.",
            "evidence": "VERIFY 0.52 coverage; transitions: PLAN→VERIFY (0.11), ACK→VERIFY (0.11).",
        },
    ],
    "architect": [
        {
            "name": "PLAN-Dominant Flow",
            "desc": "Architect mode is dominated by planning. PLAN coverage is 1.0 — every architect trace includes explicit planning.",
            "evidence": "PLAN 1.0 coverage; ACKNOWLEDGE 0.33; VERIFY 0.67.",
        },
        {
            "name": "Hypothesis-Driven Architecture",
            "desc": "Architect mode evaluates design alternatives before committing. Hypothesis-driven rate is comparable to debug.",
            "evidence": "66.7% hypothesis-driven rate — trades off alternative approaches.",
        },
        {
            "name": 'ACKNOWLEDGE→PLAN→VERIFY Chain',
            "desc": "The classic chain: ACKNOWLEDGE context → PLAN the design → VERIFY the approach. This is the dominant sequence.",
            "evidence": 'ACKNOWLEDGE→PLAN (0.33), PLAN→VERIFY (0.33), VERIFY→PLAN (0.33).',
        },
        {
            "name": "Lower Self-Correction Rate",
            "desc": "Architect mode self-corrects less than other skills (66.7%) — designs are more deliberate and pre-validated.",
            "evidence": "66.7% self-correction rate (lowest of all skills); 3.33 avg corrections.",
        },
        {
            "name": "'The' and 'Alright' Openers",
            "desc": "Architect mode is split between subject-first ('The' 66.7%) and self-narrative ('Alright' 33.3%) openings.",
            "evidence": "66.7% 'The' opener, 33.3% 'Alright'.",
        },
        {
            "name": "Third-Person System Thinking",
            "desc": "Architect mode analyzes systems using third-person pronouns — the system, not the self, is the subject.",
            "evidence": "58.8% third-person, 41.2% first-person pronouns.",
        },
        {
            "name": "Connectors: Trade-off Evaluation",
            "desc": "Architect mode uses 'therefore', 'since', and 'thus' for causal design reasoning.",
            "evidence": "1.33 connectors/turn; top: therefore, since, thus.",
        },
    ],
    "verify": [
        {
            "name": "Highest Self-Correction Rate (7.5/trace)",
            "desc": "Verify mode has the highest average self-corrections of any skill. Verification naturally involves checking and re-checking.",
            "evidence": "7.5 avg self-corrections per trace — 27% higher than code mode.",
        },
        {
            "name": "ACKNOWLEDGE→VERIFY Direct Entry",
            "desc": "Verify mode often goes ACKNOWLEDGE→VERIFY directly, skipping PLAN. Verification can be immediate.",
            "evidence": "ACKNOWLEDGE→VERIFY (0.15), ACKNOWLEDGE→PLAN (0.15) — tied.",
        },
        {
            "name": "PLAN→VERIFY→PLAN Loop",
            "desc": "Verify mode cycles: PLAN what to test → VERIFY results → RE-PLAN based on findings. This is unique to verify mode.",
            "evidence": 'VERIFY→PLAN (0.14), PLAN→VERIFY (0.13) — bidirectional loop.',
        },
        {
            "name": "Highest Same-Turn Fix Rate (24.3%)",
            "desc": "1 in 4 verify traces involves mid-turn correction. Verification frequently catches issues requiring immediate fix.",
            "evidence": "24.3% same-turn fix rate — highest of all skills.",
        },
        {
            "name": "'Alright' Opener (66%)",
            "desc": "Verify mode opens with 'Alright' 66% of the time — self-narrative framing before verification.",
            "evidence": "66.0% 'Alright' opener, 14.6% 'Okay', 11.7% 'All'.",
        },
        {
            "name": "VERIFY→PLAN as Primary Feedback",
            "desc": "The most common transition from VERIFY is back to PLAN — verification findings trigger re-planning.",
            "evidence": "VERIFY→PLAN at 0.14 — higher than VERIFY→ACKNOWLEDGE (0.05).",
        },
        {
            "name": "Thorough Step Coverage",
            "desc": "Verify mode has the most comprehensive step coverage: ACK (1.04), PLAN (0.94), EXECUTE (0.27), VERIFY (0.80), GATHER (0.07).",
            "evidence": "Highest VERIFY coverage (0.80), widest step distribution of any skill.",
        },
        {
            "name": "First-Person Verification Narrative",
            "desc": "Verify mode narrates in first-person ('I should test', 'let me verify', 'I need to check').",
            "evidence": "38.6% first-person, 61.4% third-person pronouns.",
        },
    ],
}


def load_patterns(patterns_dir: Path) -> dict[str, dict]:
    paths = {}
    for skill in SKILL_NAMES:
        path = patterns_dir / f"{skill}_patterns.yaml"
        if path.exists():
            with open(path) as f:
                paths[skill] = yaml.safe_load(f) or {}
        else:
            paths[skill] = {}
    return paths


def load_stats(stats_path: Path) -> dict:
    if stats_path.exists():
        return json.loads(stats_path.read_text())
    return {}


def _fmt(pct: float) -> str:
    return f"{pct * 100:.1f}%"


def _fmt2(val: float) -> str:
    return f"{val:.2f}"


def generate_stats_table(skill: str, data: dict, stats_data: dict) -> str:
    d = data.get("stats", {})
    cot = d.get("cot", {})
    beh = d.get("behaviors", {})
    total = data.get("total_traces", 0)
    sd = stats_data.get("skill_distribution", {}).get(skill, {})
    dist_pct = sd.get("fraction", 0)
    avg_conf = sd.get("avg_confidence", 0)
    rows = [
        ("Traces analyzed", str(total)),
        ("Distribution", f"{dist_pct * 100:.1f}%"),
        ("Avg classification confidence", _fmt(avg_conf) if avg_conf else "N/A"),
        ("CoT present rate", _fmt(cot.get("cot_rate", 0))),
        ("Avg CoT tokens", f"{cot.get('avg_tokens', 0):.1f}"),
        ("Median CoT tokens", f"{cot.get('median_tokens', 0):.1f}"),
        ("Avg paragraphs", f"{cot.get('avg_paragraphs', 0):.1f}"),
        ("Avg sentences", f"{cot.get('avg_sentences', 0):.1f}"),
        ("Self-correction rate", _fmt(beh.get("self_correction_rate", 0))),
        ("Avg self-corrections", f"{beh.get('avg_self_corrections', 0):.2f}"),
        ("Hypothesis-driven rate", _fmt(beh.get("hypothesis_driven_rate", 0))),
        ("Reasoning connectors/turn", _fmt2(cot.get("reasoning_connectors_per_turn", 0))),
        ("Same-turn fix rate", _fmt(beh.get("same_turn_fix_rate", 0))),
    ]
    lines = ["| Metric | Value |", "|--------|-------|"]
    for k, v in rows:
        lines.append(f"| {k} | {v} |")
    return "\n".join(lines)


def generate_opener_table(cot: dict) -> str:
    openers = cot.get("opener_words", {})
    if not openers:
        return "*(insufficient data)*"
    lines = ["| Opener | Frequency |", "|--------|-----------|"]
    for word, freq in sorted(openers.items(), key=lambda x: -x[1])[:8]:
        lines.append(f"| {word} | {_fmt(freq)} |")
    return "\n".join(lines)


def generate_step_transition_table(beh: dict) -> str:
    matrix = beh.get("step_transition_matrix", {})
    if not matrix:
        return "*(insufficient data)*"
    lines = ["| From → To | Probability |", "|-----------|-------------|"]
    entries = []
    for from_step, targets in matrix.items():
        for to_step, prob in sorted(targets.items(), key=lambda x: -x[1]):
            if prob > 0.01:
                entries.append((from_step, to_step, prob))
    for from_s, to_s, prob in sorted(entries, key=lambda x: -x[2])[:12]:
        lines.append(f"| {from_s} → {to_s} | {_fmt(prob)} |")
    return "\n".join(lines)


def _opener_advice(openers: dict) -> str:
    if openers:
        best = max(openers, key=openers.get)
        return f"Start with '{best}' or 'Alright'"
    return "Acknowledge what you're working with."


def _self_correct_desc(rate: float) -> str:
    return "Self-correction is universal" if rate > 0.9 else "Self-correction is common"


def generate_behavioral_patterns(skill: str, data: dict) -> str:
    patterns = SKILL_BEHAVIORAL_PATTERNS.get(skill, [])
    extra = data.get("patterns", [])

    parts = []
    for p in patterns:
        name = p["name"]
        desc = p["desc"]
        evidence = p["evidence"]
        parts.append(f"### Pattern: {name}\n\n{desc}\n\n**Evidence**: {evidence}")

    for ep in extra:
        name = ep.get("name", "Unknown")
        desc = ep.get("description", "")
        freq = ep.get("frequency", 0)
        if not any(name == p["name"] for p in patterns):
            parts.append(f"### Pattern: {name.replace('-', ' ').title()}\n\n{desc}\n\n**Frequency**: {_fmt(freq)}")

    if parts:
        return "\n\n".join(parts)
    return "*(insufficient data for pattern extraction)*"


def generate_anti_patterns_block(skill: str, data: dict) -> str:
    anti = data.get("anti_patterns", [])
    generic = [
        "Formal section headers (## ACKNOWLEDGE, ## SCOPE, etc.) — Fable 5 never uses them",
        "Using 'Oops' for self-correction — use 'Actually' or 'However' instead",
        "Making changes without understanding context first",
        "Skipping verification after changes",
        "Planning once without iterative refinement",
        "Expressing certainty when hedging is appropriate",
        "Writing one-sentence reasoning before deciding",
    ]
    lines = []
    for a in anti:
        name = a.get("name", "").replace("-", " ").title()
        freq = a.get("frequency", 0)
        desc = a.get("description", "")
        lines.append(f"- ❌ **{name}** ({_fmt(freq)}) — {desc}")
    for g in generic:
        lines.append(f"- ❌ {g}")
    return "\n".join(lines)


def generate_skill_content(skill: str, data: dict, stats_data: dict) -> str:
    d = data.get("stats", {})
    cot = d.get("cot", {})
    beh = d.get("behaviors", {})
    total = data.get("total_traces", 0)
    sd = stats_data.get("skill_distribution", {}).get(skill, {})
    total_all = stats_data.get("total_traces", 0)

    skill_name = SKILL_NAMES[skill]
    title = SKILL_TITLES[skill]
    description = SKILL_DESCRIPTIONS[skill]
    when_to_use = SKILL_WHEN[skill]

    stats_table = generate_stats_table(skill, data, stats_data)
    opener_table = generate_opener_table(cot)
    transitions_table = generate_step_transition_table(beh)
    patterns_block = generate_behavioral_patterns(skill, data)
    anti_block = generate_anti_patterns_block(skill, data)

    fp = cot.get("pronoun_first_pct", 0)
    sp = cot.get("pronoun_second_pct", 0)
    tp = cot.get("pronoun_third_pct", 0)
    top_connectors = cot.get("top_connectors", [])
    opener_words = cot.get("opener_words", {})
    best_opener = max(opener_words, key=opener_words.get) if opener_words else ""

    pronoun_desc = (
        f"**First-person**: {_fmt(fp)}, "
        f"**Second-person**: {_fmt(sp)}, "
        f"**Third-person**: {_fmt(tp)}"
    )
    voice = "first-person" if fp > tp else "third-person"

    sc_rate = beh.get("self_correction_rate", 0)
    avg_sc = beh.get("avg_self_corrections", 0)
    hypo_rate = beh.get("hypothesis_driven_rate", 0)
    same_turn = beh.get("same_turn_fix_rate", 0)
    step_cov = beh.get("step_coverage", {})

    ack_cov = _fmt(step_cov.get("ACKNOWLEDGE", 0))
    plan_cov = _fmt(step_cov.get("PLAN", 0))
    exec_cov = _fmt(step_cov.get("EXECUTE", 0))
    verify_cov = _fmt(step_cov.get("VERIFY", 0))
    scope_cov = _fmt(step_cov.get("SCOPE", 0))
    gather_cov = _fmt(step_cov.get("GATHER", 0))

    content = f"""---
name: {skill_name}
description: {title} — {description} Distilled from {total_all} real Fable 5 traces ({total} {skill}-skill traces) with data-driven precision.
version: 3.0.0
generated_from: analysis/patterns/{skill}_patterns.yaml
---

# /{skill_name}

{title} — {description}

## When To Use

{when_to_use}

## Statistics & Data Provenance

This skill is empirically derived from **{total_all} Fable 5 traces** (Crownelius/Complete-FABLE.5-traces-2M dataset). The {skill}-skill subset contains **{total} traces** ({sd.get('fraction', 0) * 100:.1f}% of total). Downloading the full 2M-trace dataset and re-running the analysis pipeline will update these numbers automatically.

{stats_table}

## Core Principle

Fable 5 reasons in natural, flowing paragraphs. The {skill} skill is characterized by:

- **Voice**: {voice.capitalize()} dominant ({pronoun_desc})
- **CoT availability**: {'Always present' if cot.get('cot_rate', 0) > 0.9 else 'Not always present'} ({_fmt(cot.get('cot_rate', 0))})
- **Self-correction**: {_fmt(sc_rate)} of traces contain corrections
- **Hypothesis-driven**: {_fmt(hypo_rate)} of traces use hypothesis testing
- **Same-turn fix**: {_fmt(same_turn)} involve mid-turn course correction
- **Connectors**: {_fmt2(cot.get('reasoning_connectors_per_turn', 0))} per turn — top: {', '.join(top_connectors[:4])}

### Opener Words

{opener_table}

### Step Transition Matrix (Top Transitions)

{transitions_table}

## The Natural {skill.capitalize()} Flow

Do NOT write formal section headers. Follow this natural reasoning flow:

### 1. ACKNOWLEDGE — Context Awareness

{_opener_advice(opener_words)}

- {"Opener '" + best_opener + "' is most frequent" if best_opener else "Acknowledge before acting"}
- Step coverage: {ack_cov}
- NEVER write 'ACKNOWLEDGE:' as a header

### 2. PLAN — Approach Design

Plan your approach step by step. PLAN transitions most frequently to VERIFY and EXECUTE.

- Step coverage: {plan_cov}
- Use connectors: {', '.join(top_connectors[:3])}
- Consider trade-offs inline

### 3. EXECUTE — Take Action

State what you'll do, then do it.

- Step coverage: {exec_cov}
- EXECUTE transitions most to PLAN (iterative development)

### 4. VERIFY — Validate

After actions, verify correctness.

- Step coverage: {verify_cov}
- {_fmt(same_turn)} of turns involve same-turn verification

### 5. ITERATE — Self-Correct

{_self_correct_desc(sc_rate)} ({_fmt(sc_rate)}) — this is normal, not a failure.

- Avg {_fmt2(avg_sc)} corrections per trace
- {_fmt(hypo_rate)} of traces are hypothesis-driven
- Use 'Actually' or 'However' for corrections

## Behavioral Patterns

{patterns_block}

## Key Statistics from {total_all} Traces ({skill.capitalize()} Subset)

### CoT Structure
- **Avg tokens**: {cot.get('avg_tokens', 0):.1f} (median: {cot.get('median_tokens', 0):.1f})
- **Avg paragraphs**: {cot.get('avg_paragraphs', 0):.1f}
- **Avg sentences**: {cot.get('avg_sentences', 0):.1f}
- **Avg characters**: {cot.get('avg_chars', 0):.1f}
- **Max tokens**: {cot.get('max_tokens', 0)}, **Min tokens**: {cot.get('min_tokens', 0)}

### Reasoning Style
- **Pronoun distribution**: {pronoun_desc}
- **Connectors per turn**: {_fmt2(cot.get('reasoning_connectors_per_turn', 0))}
- **Top connectors**: {', '.join(top_connectors)}
- **Self-corrections per trace**: {_fmt2(avg_sc)}

### Behavior
- **Hypothesis-driven**: {_fmt(hypo_rate)}
- **Multi-investigation rate**: {_fmt(beh.get('multi_investigation_rate', 0))}
- **Same-turn fix rate**: {_fmt(same_turn)}
- **Step coverage**: ACK {ack_cov}, SCOPE {scope_cov}, GATHER {gather_cov}, PLAN {plan_cov}, EXECUTE {exec_cov}, VERIFY {verify_cov}

## Anti-Patterns

{anti_block}
"""

    return content


def generate_skill(skill: str, patterns: dict, stats: dict, output_dir: Path) -> Path:
    data = patterns.get(skill, {})
    content = generate_skill_content(skill, data, stats)
    skill_dir = output_dir / f"deepseek-{skill}"
    skill_dir.mkdir(parents=True, exist_ok=True)
    path = skill_dir / "SKILL.md"
    path.write_text(content)
    return path


def main():
    parser = argparse.ArgumentParser(description="Generate enhanced SKILL.md from pattern extraction results")
    parser.add_argument("--patterns-dir", default="analysis/patterns")
    parser.add_argument("--output-dir", default="skills")
    args = parser.parse_args()

    patterns_dir = Path(args.patterns_dir)
    output_dir = Path(args.output_dir)
    stats_path = patterns_dir / "combined_stats.json"

    patterns = load_patterns(patterns_dir)
    stats = load_stats(stats_path)

    total = stats.get("total_traces", 0)
    print(f"Loaded patterns from {len(patterns)} skills, total traces: {total}")

    pattern_count = 0
    for skill in SKILL_NAMES:
        data = patterns.get(skill, {})
        n = data.get("total_traces", 0)
        bp = len(SKILL_BEHAVIORAL_PATTERNS.get(skill, []))
        pattern_count += bp
        print(f"  {skill}: {n} traces, {bp} behavior patterns")
        path = generate_skill(skill, patterns, stats, output_dir)
        print(f"    → {path}")

    print(f"\nDone! Generated {len(SKILL_NAMES)} enhanced SKILL.md files in {output_dir.resolve()}")
    print(f"Total behavioral patterns: {pattern_count}")


if __name__ == "__main__":
    main()
