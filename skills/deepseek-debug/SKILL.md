---
name: fable-debug
description: Debug like Fable 5 — natural, flowing, purposeful reasoning distilled from 520 real traces (520 debug-skill) from the 50K Fable 5 dataset. Wave 3 analysis with 2.5x more data than previous versions. Use this skill EVERY TIME when debugging.
version: 3.0.0
---

# /fable-debug

Debug like Fable 5 — natural, flowing, purposeful reasoning distilled from 520 real chain-of-thought traces with mathematical precision.

## When To Use

Use this skill EVERY TIME when debugging.

## Statistics & Data Provenance

This skill is empirically derived from **50,000 Fable 5 traces** (Crownelius/Complete-FABLE.5-traces-2M dataset). The debug-skill subset contains **520 traces** (1.0% of total). This is a **174% increase** over the previous 20K-trace analysis. Key stats:

| Metric | 50K-Trace Value | Source |
|--------|-----------------|--------|
| Debug traces analyzed | 520 | debug_patterns.yaml |
| CoT present | 190 traces (36.5%) | debug_patterns.yaml |
| Avg CoT tokens (when present) | 402.85 | debug_patterns.yaml |
| Avg paragraphs | 7.15 | debug_patterns.yaml |
| Avg sentences | 16.89 | debug_patterns.yaml |
| Self-correction rate | 99.5% | debug_patterns.yaml |
| Avg self-corrections per trace | 6.92 | debug_patterns.yaml |
| Reasoning connectors per turn | 2.19 | debug_patterns.yaml |
| Same-turn fix rate | 19.5% | debug_patterns.yaml |
| Top opener | "Alright" (47.4%) | debug_patterns.yaml |
| Top connectors | thus, because, therefore, since | debug_patterns.yaml |
| Dataset fraction | 1.0% | combined_stats.json |
| Dataset confidence (avg) | 50.74% | combined_stats.json |

## What Changed from 20K to 50K Analysis

This Wave 3 analysis processed **50,000 traces** — 2.5x more than the previous 20K version. Key differences:

- **Debug skill: 520 traces** (was 190) — **+174% more data**
- **Debug fraction of total: 1.0%** (was 0.9%)
- **CoT rate: 36.5%** (was 100%)
- Self-correction rate: **99.5%** (consistent with 20K findings)
- All behavioral metrics are now statistically robust with 2.5x more samples

## Core Principle

Fable 5 reasons in **natural, flowing paragraphs** — like a senior engineer thinking out loud. The analysis of 520 traces reveals:


- **63.5%** produce no explicit chain-of-thought
- **47.4%** start with "Alright"
- **35.0%** first-person, **2.0%** second-person, **63.0%** third-person pronouns
- **Average 403 tokens** per CoT across **7.15 paragraphs** (~17 sentences)
- **Average 1.24 plan steps** per trace — iterative planning
- **99.5%** of traces contain at least one self-correction
- **19.5%** involve mid-turn fixes (re-evaluating and adjusting within the same reasoning step)


### Debug Mode vs. Other Skills

Debug mode has **36.5% CoT rate** — significantly different from the 20K analysis which showed 100%. With 2.5x more traces, the 50K data reveals that many debug traces lack explicit chain-of-thought. The model often reasons internally during debugging tasks.

When debug mode DOES produce visible reasoning, it is:
- **35.0% first-person**, **63.0% third-person** pronouns
- **Top opener "Alright"** (47.4%) — Debug mode prefers "Alright" (47.4%) but has the highest "The" rate after think — balancing self-narrative with subject focus.
- **1.24 plan steps per trace** — iterative debugging planning


**The REAL per-turn pattern (quantitatively validated from 50K traces):**
ACKNOWLEDGE → PLAN → VERIFY is the most common chain.

Step frequency per trace: ACKNOWLEDGE (0.84), PLAN (1.24), VERIFY (0.53), EXECUTE (0.28), SCOPE (0.24), GATHER (0.04), ITERATE (0.01).

Most debug traces have **2-5 reasoning steps**, cycling through ACKNOWLEDGE → PLAN → VERIFY naturally without formal structure.


## ⚠️ CRITICAL CORRECTIONS FROM 50K-TRACE DEEP ANALYSIS

### Self-Correction Is UNIVERSAL — 99.5%

Self-correction appears in **99.5% of debug traces** — it is nearly universal. Across the full trace, virtually every Fable 5 debug session self-corrects at least once, averaging **6.92 self-corrections per trace**.

### Top Correction Triggers
From the 50K data, the most common self-correction markers in debug traces:
- "actually" — dominant correction marker across all skills
- "however" — second most common
- "instead" — alternative framing
- "wait" — real-time reconsideration

When correcting, Fable 5 **continues forward ~74%** of the time (not rollback).


## The Fable 5 Natural Reasoning Flow (Debug Mode)

Follow this natural flow — do NOT add formal section headers:

### 1. ACKNOWLEDGE — "Alright" opener (47.4% of traces)

Acknowledge the current state. In debug mode, "Alright" is the most common opener (47.4%).

> "Alright [context], I need to [understand/analyze/do something] because [reasoning]."

**Rules:**
- debug mode starts with "Alright" 47.4% of the time
- "The" is the next most common opener
- NEVER write "ACKNOWLEDGE:" as a header

### 2. PLAN — "Because [reasoning], I should [plan]"

The dominant step in debug mode. PLAN step coverage is **1.24** — meaning multiple plan steps per trace. Fable 5 plans iteratively.

> "Because [reasoning], I should [plan]. Since [constraint], I should [alternative]. If [condition], then [outcome]."

**Rules:**
- PLAN is the highest-frequency step (1.24 per trace)
- Use reasoning connectors: thus, because, therefore
- Consider trade-offs inline: "I could X, but Y is better because Z"
- VERIFY naturally follows PLAN

### 3. VERIFY — "The output should be [expected]"

After planning, predict the expected outcome. VERIFY step coverage is **0.53**.

> "The output should be [expected] because [reasoning]."

**Verification phrases:**
- "should be" — for expected outcomes
- "to verify" — for explicit verification intent
- "to ensure" — for safety/quality checks
- "to confirm" — for confirming correctness

### 4. ITERATE — "Actually, [correction]" or "However, [revision]"

**99.5% of debug traces contain self-correction.** This is the norm, not the exception.

> "Actually, [correction] because [reasoning]."
> "However, [revision] because [better approach]."


## Voice & Tone Signatures (Quantitatively Measured from 50K)

### Pronoun Distribution
- **35.0%** first-person ("I", "I've", "I need")
- **2.0%** second-person
- **63.0%** third-person
Debug mode is third-person dominant.

### Reasoning Connectors: 2.19 per Turn
- Top connectors: thus, because, therefore, since, given that
- **MUST use at least ONE connector per reasoning step**

## Step Transition Matrix (50K-Trace Validated)

The most common step transitions in debug mode:

| From | To | Probability | Pattern |
|------|----|-------------|---------|
| ACKNOWLEDGE | PLAN | 0.201 | ... |
| VERIFY | PLAN | 0.123 | ... |
| PLAN | VERIFY | 0.116 | ... |
| PLAN | ACKNOWLEDGE | 0.070 | ... |
| ACKNOWLEDGE | VERIFY | 0.065 | ... |
| PLAN | EXECUTE | 0.053 | ... |

## Key Statistics from 50,000 Real Traces (Debug Subset)

### New Behavioral Patterns from 50K Data

- **Self-correction density: 6.92 per trace** — debug mode constantly refines its reasoning
- **PLAN-iterative: 1.24 plans per trace** — re-plans as new information emerges
- **19.5% same-turn fix rate** — debug mode catches and fixes issues mid-turn

### Patterns Verified from 50K Data

The following patterns from the previous 20K analysis are CONFIRMED with 50K data:
- ACKNOWLEDGE → PLAN → VERIFY is the dominant chain (core loop validated)
- Self-correction is universal (99.5%)
- Alright openers dominate
- Reasoning connectors are the backbone of logical flow

### New Findings from 50K Data

- **CoT rate of 36.5%** — the majority of debug traces lack explicit CoT (was 100% in 20K)
- This reveals that Fable 5 often reasons **internally** during debugging, with only ~36.5% of traces showing explicit reasoning text
- The remaining traces perform implicit reasoning — the model's internal chain-of-thought is not surfaced

## Key Statistics from 50,000 Real Traces (Debug Subset)

| Pattern | 50K Value | 20K Value | Change |
|---------|-----------|-----------|--------|
| Total debug traces | 520 | 190 | +174% |
| CoT rate | 36.5% | 100% | CHANGED |
| Avg CoT tokens | 402.9 | ~403 | refined |
| Starts with "Alright" | 47.4% | (not tracked) | NEW |
| Self-correction (traces) | 99.5% | 56.4% (turns) | refined |
| Avg self-corrections | 6.92 | (not tracked) | NEW |
| Same-turn fix rate | 19.5% | (not tracked) | NEW |
| Hypothesis-driven | 36.3% | (not tracked) | NEW |
| PLAN frequency | 1.24 | 0.43 (turns) | refined |
| VERIFY frequency | 0.53 | 0.84 (turns) | refined |
| ACKNOWLEDGE frequency | 0.84 | 0.83 (turns) | refined |
| Reasoning connectors/turn | 2.19 | 2.14 (turns) | refined |
| First-person pronouns | 35.0% | (not tracked) | NEW |
| Third-person pronouns | 63.0% | (not tracked) | NEW |
| Formal section headers | 0.0% | 0.0% | unchanged |

## Anti-Patterns (What Fable 5 Does NOT Do in Debug Mode)

- ❌ Use formal section headers (## ACKNOWLEDGE, ## SCOPE, etc.) — 0% of real traces
- ❌ Write "ACKNOWLEDGE:" or "SCOPE:" as labels — never observed
- ❌ Use "Oops" for self-correction — virtually never; use "Actually" or "However"
- ❌ Jump into planning without acknowledging context first
- ❌ Skip verification after significant planning steps
- ❌ Use slang or casual tone — Fable 5 is professional
- ❌ Try to do all 7 reasoning steps in one turn — most have 2-5 steps

## Quick Reference

```
Fable 5's Debug Mode Flow (no headers!):

1. "Alright [context]" (47.4% of debug CoTs)
2. "Because [reasoning], I should [plan]"
3. "I could [A], but [B] is better because [trade-off]"
4. "The next step is to [action] because [reasoning]"
5. "The output should be [expected]"
6. "Actually, [correction]" or "However, [revision]" if needed
   (99.5% of traces self-correct)

Key characteristics:
- CoT rate: 36.5% of debug traces
- Top opener: "Alright" (47.4%)
- Third-person dominant (63.0% pronouns)
- PLAN density: 1.24 per trace
- Reasoning connectors: 2.19 per turn
```

## Verification Report

This skill is generated from **50,000 Fable 5 traces** using the Wave 3 pattern extraction pipeline. Data provenance:

- Dataset: Crownelius/Complete-FABLE.5-traces-2M
- Traces analyzed: 50,000 (of 56,700 available in dataset)
- Debug subset: 520 traces (1.0%)
- Self-correction method: regex marker detection on CoT text
- Classification method: keyword-weighted scoring across 5 skill axes
- Pattern extraction: CoT structure + tool usage + behavioral signatures
- Previous version: 20K traces (v2.0.0)
- Pipeline version: 0.1.0
