#!/usr/bin/env python3
"""Generate enhanced SKILL.md files from 50K-trace pattern analysis."""

import json
import yaml
from pathlib import Path

PATTERNS_DIR = Path("analysis/patterns")
SKILLS_DIR = Path("skills")

def _pct(v):
    return f"{v * 100:.1f}%"

def _fmt(v, d=1):
    return f"{v:.{d}f}"

def _frac(n, total):
    return f"{(n / total) * 100:.1f}%"


def generate_skill(skill: str, stats: dict, yaml_data: dict) -> str:
    total = stats["total_traces"]
    c_per = stats["per_skill"][skill]
    c_dist = stats["skill_distribution"].get(skill, {})
    y = yaml_data["stats"]
    cot = y["cot"]
    tool = y["tool_usage"]
    beh = y["behaviors"]
    pats = yaml_data.get("patterns", [])
    anti = yaml_data.get("anti_patterns", [])
    step_cov = beh.get("step_coverage", {})
    n = c_per["trace_count"]

    openers = cot.get("opener_words", {})
    sc_rate = beh.get("self_correction_rate", 0)
    avg_sc = beh.get("avg_self_corrections", 0)
    h_rate = beh.get("hypothesis_driven_rate", 0)
    conn = cot.get("reasoning_connectors_per_turn", 0)

    titles = {
        "think": ("Think like Fable 5", "Natural, flowing, purposeful reasoning distilled from chain-of-thought traces"),
        "code": ("Code like Fable 5", "Methodical, verified, and deeply informed by context"),
        "debug": ("Debug like Fable 5", "Root-cause analysis and fix — hypothesis-driven, systematic, and verification-focused"),
        "architect": ("Architect like Fable 5", "System decomposition and design — planning interfaces before implementation"),
        "verify": ("Verify like Fable 5", "Self-verification and test generation — thorough validation before declaring done"),
    }
    when = {
        "think": "Use this skill EVERY TIME before writing code, making decisions, or taking action.",
        "code": "Use this skill whenever you need to write, edit, or create code.",
        "debug": "Use this skill when debugging — crashes, silent failures, wrong output, edge-case bugs.",
        "architect": "Use this skill when designing systems, choosing architectures, or planning component structure.",
        "verify": "Use this skill when writing tests, validating output, or reviewing code for correctness.",
    }

    title, subtitle = titles.get(skill, ("Fable 5 Skill", ""))
    tm = beh.get("step_transition_matrix", {})

    gen_pat = "".join(f"""### Pattern: {p["name"].replace("-", " ").title()}

{p.get("description", "")}

**Frequency**: {_pct(p.get("frequency", 0))}

""" for p in pats)

    gen_anti = "".join(f"- ❌ **{a['name'].replace('-', ' ').title()}** ({_pct(a.get('frequency', 0))}) — {a.get('description', '')}\n" for a in anti)
    gen_anti += "- ❌ Formal section headers (## ACKNOWLEDGE, ## SCOPE, etc.) — Fable 5 never uses them\n"
    gen_anti += "- ❌ Using 'Oops' for self-correction — use 'Actually' or 'However' instead\n"
    gen_anti += "- ❌ Making changes without understanding context first\n"
    gen_anti += "- ❌ Skipping verification after changes\n"
    gen_anti += "- ❌ Planning once without iterative refinement\n"
    gen_anti += "- ❌ Expressing certainty when hedging is appropriate\n"
    gen_anti += "- ❌ Writing one-sentence reasoning before deciding\n"

    tm_lines = []
    for f in sorted(tm.keys())[:5]:
        for t, p in sorted(tm[f].items(), key=lambda x: -x[1])[:4]:
            tm_lines.append(f"| {f} → {t} | {_pct(p)} |\n")

    opener_rows = "".join(f"| {w} | {_pct(f)} |\n" for w, f in list(openers.items())[:8])
    top_opener = list(openers.keys())[0] if openers else ""
    top_opener_pct = _pct(list(openers.values())[0]) if openers else "0%"

    return f"""---
name: fable-{skill}
description: {title} — {subtitle}. Distilled from {n:,} real Fable 5 traces ({skill}-skill subset) with data-driven precision.
version: 3.0.0
generated_from: analysis/patterns/{skill}_patterns.yaml
---

# /fable-{skill}

{title} — {subtitle}.

## When To Use

{when.get(skill, "")}

## Statistics & Data Provenance

This skill is empirically derived from **{total:,} Fable 5 traces** (Crownelius/Complete-FABLE.5-traces-2M dataset). The {skill}-skill subset contains **{n:,} traces** ({_frac(n, total)} of total). Re-running the analysis pipeline on the full 2M-trace dataset will update these numbers automatically.

| Metric | 50K-Trace Value |
|--------|-----------------|
| Traces analyzed | {n:,} |
| Distribution | {_frac(n, total)} |
| Avg classification confidence | {_pct(c_dist.get("avg_confidence", 0))} |
| CoT present rate | {_pct(cot.get("cot_rate", 0))} |
| Avg CoT tokens | {_fmt(cot.get("avg_tokens", 0))} |
| Median CoT tokens | {cot.get("median_tokens", 0)} |
| Avg paragraphs | {_fmt(cot.get("avg_paragraphs", 0))} |
| Avg sentences | {_fmt(cot.get("avg_sentences", 0))} |
| Self-correction rate | {_pct(sc_rate)} |
| Avg self-corrections | {_fmt(avg_sc)} |
| Hypothesis-driven rate | {_pct(h_rate)} |
| Reasoning connectors/turn | {_fmt(conn)} |
| Same-turn fix rate | {_pct(beh.get("same_turn_fix_rate", 0))} |
| Tool calls/trace | {_fmt(tool.get("avg_tool_calls", 0))} |

## Core Principle

Fable 5 reasons in natural, flowing paragraphs. The {skill} skill is characterized by:

- **Voice**: Third-person dominant (**First-person**: {_pct(cot.get("pronoun_first_pct", 0))}, **Second-person**: {_pct(cot.get("pronoun_second_pct", 0))}, **Third-person**: {_pct(cot.get("pronoun_third_pct", 0))})
- **CoT availability**: {_pct(cot.get("cot_rate", 0))} of traces contain explicit CoT
- **Self-correction**: {_pct(sc_rate)} of traces contain corrections
- **Hypothesis-driven**: {_pct(h_rate)} of traces use hypothesis testing
- **Same-turn fix**: {_pct(beh.get("same_turn_fix_rate", 0))} involve mid-turn course correction
- **Connectors**: {_fmt(conn)} per turn — top: {", ".join(cot.get("top_connectors", [])[:5])}

### Opener Words

| Opener | Frequency |
|--------|-----------|
{opener_rows}
### Step Transition Matrix (Top Transitions)

| From → To | Probability |
|-----------|-------------|
{"".join(tm_lines)}
## The Natural {skill.title()} Flow

Do NOT write formal section headers. Follow this natural reasoning flow:

### 1. ACKNOWLEDGE — Context Awareness

Start with '{top_opener}'

- Opener '{top_opener}' is most frequent ({top_opener_pct})
- Step coverage: {_pct(step_cov.get("ACKNOWLEDGE", 0))}
- NEVER write 'ACKNOWLEDGE:' as a header

### 2. PLAN — Approach Design

Plan your approach step by step. PLAN transitions most frequently to VERIFY and EXECUTE.

- Step coverage: {_pct(step_cov.get("PLAN", 0))}
- Use connectors: {", ".join(cot.get("top_connectors", [])[:4])}
- Consider trade-offs inline

### 3. EXECUTE — Take Action

State what you'll do, then do it.

- Step coverage: {_pct(step_cov.get("EXECUTE", 0))}
- EXECUTE transitions most to PLAN (iterative development)

### 4. VERIFY — Validate

After actions, verify correctness.

- Step coverage: {_pct(step_cov.get("VERIFY", 0))}
- {_pct(beh.get("same_turn_fix_rate", 0))} of turns involve same-turn verification

### 5. ITERATE — Self-Correct

Self-correction is near-universal ({_pct(sc_rate)}) — this is normal, not a failure.

- Avg {_fmt(avg_sc)} corrections per trace
- {_pct(h_rate)} of traces are hypothesis-driven
- Use 'Actually' or 'However' for corrections

## Behavioral Patterns ({len(pats)} patterns)

{gen_pat}
## Anti-Patterns ({len(anti)} anti-patterns)

{gen_anti}
## Key Statistics from {n:,} Traces ({skill.title()} Subset)

### CoT Structure
- **Avg tokens**: {_fmt(cot.get("avg_tokens", 0))} (median: {cot.get("median_tokens", 0)})
- **Avg paragraphs**: {_fmt(cot.get("avg_paragraphs", 0))}
- **Avg sentences**: {_fmt(cot.get("avg_sentences", 0))}
- **Avg characters**: {_fmt(cot.get("avg_chars", 0))}
- **Max tokens**: {cot.get("max_tokens", 0)}, **Min tokens**: {cot.get("min_tokens", 0)}

### Reasoning Style
- **Pronoun distribution**: **First-person**: {_pct(cot.get("pronoun_first_pct", 0))}, **Second-person**: {_pct(cot.get("pronoun_second_pct", 0))}, **Third-person**: {_pct(cot.get("pronoun_third_pct", 0))}
- **Connectors per turn**: {_fmt(conn)}
- **Top connectors**: {", ".join(cot.get("top_connectors", [])[:5])}
- **Self-corrections per trace**: {_fmt(avg_sc)}
- **Tool calls per trace**: {_fmt(tool.get("avg_tool_calls", 0))}

### Behavior
- **Hypothesis-driven**: {_pct(h_rate)}
- **Multi-investigation rate**: {_pct(beh.get("multi_investigation_rate", 0))}
- **Same-turn fix rate**: {_pct(beh.get("same_turn_fix_rate", 0))}
- **Step coverage**: ACK {_pct(step_cov.get("ACKNOWLEDGE", 0))}, SCOPE {_pct(step_cov.get("SCOPE", 0))}, GATHER {_pct(step_cov.get("GATHER", 0))}, PLAN {_pct(step_cov.get("PLAN", 0))}, EXECUTE {_pct(step_cov.get("EXECUTE", 0))}, VERIFY {_pct(step_cov.get("VERIFY", 0))}
"""


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def main():
    with open(PATTERNS_DIR / "combined_stats.json") as f:
        stats = json.load(f)

    for skill in ["think", "code", "debug", "architect", "verify"]:
        yaml_file = PATTERNS_DIR / f"{skill}_patterns.yaml"
        yaml_data = load_yaml(yaml_file)
        n = stats["per_skill"][skill]["trace_count"]

        print(f"Generating {skill} skill ({n:,} traces)...")
        content = generate_skill(skill, stats, yaml_data)

        skill_path = SKILLS_DIR / f"deepseek-{skill}" / "SKILL.md"
        skill_path.write_text(content)
        print(f"  Written: {skill_path}")


if __name__ == "__main__":
    main()
