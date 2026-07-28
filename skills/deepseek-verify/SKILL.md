---
name: fable-verify
description: Verify like Fable 5 — natural, flowing, purposeful reasoning distilled from 1,791 real traces (1,791 verify-skill) from the 50K Fable 5 dataset. Wave 3 analysis with 2.5x more data than previous versions. Use this skill EVERY TIME when verifying.
version: 3.0.0
---

# /fable-verify

Verify like Fable 5 — natural, flowing, purposeful reasoning distilled from 1,791 real chain-of-thought traces with mathematical precision.

## When To Use

Use this skill EVERY TIME when verifying.

## Statistics & Data Provenance

This skill is empirically derived from **50,000 Fable 5 traces** (Crownelius/Complete-FABLE.5-traces-2M dataset). The verify-skill subset contains **1,791 traces** (3.6% of total). This is a **92% increase** over the previous 20K-trace analysis. Key stats:

| Metric | 50K-Trace Value | Source |
|--------|-----------------|--------|
| Verify traces analyzed | 1,791 | verify_patterns.yaml |
| CoT present | 935 traces (52.2%) | verify_patterns.yaml |
| Avg CoT tokens (when present) | 391.01 | verify_patterns.yaml |
| Avg paragraphs | 6.88 | verify_patterns.yaml |
| Avg sentences | 16.14 | verify_patterns.yaml |
| Self-correction rate | 98.7% | verify_patterns.yaml |
| Avg self-corrections per trace | 6.49 | verify_patterns.yaml |
| Reasoning connectors per turn | 2.02 | verify_patterns.yaml |
| Same-turn fix rate | 26.4% | verify_patterns.yaml |
| Top opener | "Alright" (52.9%) | verify_patterns.yaml |
| Top connectors | thus, since, because, therefore | verify_patterns.yaml |
| Dataset fraction | 3.6% | combined_stats.json |
| Dataset confidence (avg) | 50.05% | combined_stats.json |

## What Changed from 20K to 50K Analysis

This Wave 3 analysis processed **50,000 traces** — 2.5x more than the previous 20K version. Key differences:

- **Verify skill: 1,791 traces** (was 935) — **+92% more data**
- **Verify fraction of total: 3.6%** (was 4.7%)
- **CoT rate: 52.2%** (was 100%)
- Self-correction rate: **98.7%** (consistent with 20K findings)
- All behavioral metrics are now statistically robust with 2.5x more samples

## Core Principle

Fable 5 reasons in **natural, flowing paragraphs** — like a senior engineer thinking out loud. The analysis of 1,791 traces reveals:


- **47.8%** produce no explicit chain-of-thought
- **52.9%** start with "Alright"
- **38.9%** first-person, **2.3%** second-person, **58.9%** third-person pronouns
- **Average 391 tokens** per CoT across **6.88 paragraphs** (~16 sentences)
- **Average 1.15 plan steps** per trace — iterative planning
- **98.7%** of traces contain at least one self-correction
- **26.4%** involve mid-turn fixes (re-evaluating and adjusting within the same reasoning step)


### Verify Mode vs. Other Skills

Verify mode has **52.2% CoT rate** — significantly different from the 20K analysis which showed 100%. With 2.5x more traces, the 50K data reveals that many verify traces lack explicit chain-of-thought. The model often reasons internally during verifying tasks.

When verify mode DOES produce visible reasoning, it is:
- **38.9% first-person**, **58.9% third-person** pronouns
- **Top opener "Alright"** (52.9%) — Verify mode is similar to code — "Alright" at 52.9%, conversational verification style.
- **1.15 plan steps per trace** — iterative verifying planning


**The REAL per-turn pattern (quantitatively validated from 50K traces):**
ACKNOWLEDGE → PLAN → VERIFY is the most common chain.

Step frequency per trace: ACKNOWLEDGE (0.84), PLAN (1.15), VERIFY (0.79), EXECUTE (0.25), SCOPE (0.08), GATHER (0.04), ITERATE (0.00).

Most verify traces have **2-5 reasoning steps**, cycling through ACKNOWLEDGE → PLAN → VERIFY naturally without formal structure.


## ⚠️ CRITICAL CORRECTIONS FROM 50K-TRACE DEEP ANALYSIS

### Self-Correction Is UNIVERSAL — 98.7%

Self-correction appears in **98.7% of verify traces** — it is nearly universal. Across the full trace, virtually every Fable 5 verify session self-corrects at least once, averaging **6.49 self-corrections per trace**.

### Top Correction Triggers
From the 50K data, the most common self-correction markers in verify traces:
- "actually" — dominant correction marker across all skills
- "however" — second most common
- "instead" — alternative framing
- "wait" — real-time reconsideration

When correcting, Fable 5 **continues forward ~74%** of the time (not rollback).


## The Fable 5 Natural Reasoning Flow (Verify Mode)

Follow this natural flow — do NOT add formal section headers:

### 1. ACKNOWLEDGE — "Alright" opener (52.9% of traces)

Acknowledge the current state. In verify mode, "Alright" is the most common opener (52.9%).

> "Alright [context], I need to [understand/analyze/do something] because [reasoning]."

**Rules:**
- verify mode starts with "Alright" 52.9% of the time
- "The" is the next most common opener
- NEVER write "ACKNOWLEDGE:" as a header

### 2. PLAN — "Because [reasoning], I should [plan]"

The dominant step in verify mode. PLAN step coverage is **1.15** — meaning multiple plan steps per trace. Fable 5 plans iteratively.

> "Because [reasoning], I should [plan]. Since [constraint], I should [alternative]. If [condition], then [outcome]."

**Rules:**
- PLAN is the highest-frequency step (1.15 per trace)
- Use reasoning connectors: thus, since, because
- Consider trade-offs inline: "I could X, but Y is better because Z"
- VERIFY naturally follows PLAN

### 3. VERIFY — "The output should be [expected]"

After planning, predict the expected outcome. VERIFY step coverage is **0.79**.

> "The output should be [expected] because [reasoning]."

**Verification phrases:**
- "should be" — for expected outcomes
- "to verify" — for explicit verification intent
- "to ensure" — for safety/quality checks
- "to confirm" — for confirming correctness

### 4. ITERATE — "Actually, [correction]" or "However, [revision]"

**98.7% of verify traces contain self-correction.** This is the norm, not the exception.

> "Actually, [correction] because [reasoning]."
> "However, [revision] because [better approach]."


## Voice & Tone Signatures (Quantitatively Measured from 50K)

### Pronoun Distribution
- **38.9%** first-person ("I", "I've", "I need")
- **2.3%** second-person
- **58.9%** third-person
Verify mode is third-person dominant.

### Reasoning Connectors: 2.02 per Turn
- Top connectors: thus, since, because, therefore, given that
- **MUST use at least ONE connector per reasoning step**

## Step Transition Matrix (50K-Trace Validated)

The most common step transitions in verify mode:

| From | To | Probability | Pattern |
|------|----|-------------|---------|
| VERIFY | PLAN | 0.190 | ... |
| ACKNOWLEDGE | PLAN | 0.180 | ... |
| PLAN | VERIFY | 0.149 | ... |
| ACKNOWLEDGE | VERIFY | 0.121 | ... |
| PLAN | ACKNOWLEDGE | 0.058 | ... |
| PLAN | EXECUTE | 0.045 | ... |

## Key Statistics from 50,000 Real Traces (Verify Subset)

### New Behavioral Patterns from 50K Data

- **Self-correction density: 6.49 per trace** — verify mode constantly refines its reasoning
- **PLAN-iterative: 1.15 plans per trace** — re-plans as new information emerges
- **26.4% same-turn fix rate** — verify mode catches and fixes issues mid-turn

### Patterns Verified from 50K Data

The following patterns from the previous 20K analysis are CONFIRMED with 50K data:
- ACKNOWLEDGE → PLAN → VERIFY is the dominant chain (core loop validated)
- Self-correction is universal (98.7%)
- Alright openers dominate
- Reasoning connectors are the backbone of logical flow

### New Findings from 50K Data

- **CoT rate of 52.2%** — the majority of verify traces lack explicit CoT (was 100% in 20K)
- This reveals that Fable 5 often reasons **internally** during verifying, with only ~52.2% of traces showing explicit reasoning text
- The remaining traces perform implicit reasoning — the model's internal chain-of-thought is not surfaced

## Key Statistics from 50,000 Real Traces (Verify Subset)

| Pattern | 50K Value | 20K Value | Change |
|---------|-----------|-----------|--------|
| Total verify traces | 1,791 | 935 | +92% |
| CoT rate | 52.2% | 100% | CHANGED |
| Avg CoT tokens | 391.0 | ~391 | refined |
| Starts with "Alright" | 52.9% | (not tracked) | NEW |
| Self-correction (traces) | 98.7% | 56.4% (turns) | refined |
| Avg self-corrections | 6.49 | (not tracked) | NEW |
| Same-turn fix rate | 26.4% | (not tracked) | NEW |
| Hypothesis-driven | 22.9% | (not tracked) | NEW |
| PLAN frequency | 1.15 | 0.43 (turns) | refined |
| VERIFY frequency | 0.79 | 0.84 (turns) | refined |
| ACKNOWLEDGE frequency | 0.84 | 0.83 (turns) | refined |
| Reasoning connectors/turn | 2.02 | 2.14 (turns) | refined |
| First-person pronouns | 38.9% | (not tracked) | NEW |
| Third-person pronouns | 58.9% | (not tracked) | NEW |
| Formal section headers | 0.0% | 0.0% | unchanged |

## Anti-Patterns (What Fable 5 Does NOT Do in Verify Mode)

- ❌ Use formal section headers (## ACKNOWLEDGE, ## SCOPE, etc.) — 0% of real traces
- ❌ Write "ACKNOWLEDGE:" or "SCOPE:" as labels — never observed
- ❌ Use "Oops" for self-correction — virtually never; use "Actually" or "However"
- ❌ Jump into planning without acknowledging context first
- ❌ Skip verification after significant planning steps
- ❌ Use slang or casual tone — Fable 5 is professional
- ❌ Try to do all 7 reasoning steps in one turn — most have 2-5 steps

## Quick Reference

```
Fable 5's Verify Mode Flow (no headers!):

1. "Alright [context]" (52.9% of verify CoTs)
2. "Because [reasoning], I should [plan]"
3. "I could [A], but [B] is better because [trade-off]"
4. "The next step is to [action] because [reasoning]"
5. "The output should be [expected]"
6. "Actually, [correction]" or "However, [revision]" if needed
   (98.7% of traces self-correct)

Key characteristics:
- CoT rate: 52.2% of verify traces
- Top opener: "Alright" (52.9%)
- Third-person dominant (58.9% pronouns)
- PLAN density: 1.15 per trace
- Reasoning connectors: 2.02 per turn
```

## Verification Report

This skill is generated from **50,000 Fable 5 traces** using the Wave 3 pattern extraction pipeline. Data provenance:

- Dataset: Crownelius/Complete-FABLE.5-traces-2M
- Traces analyzed: 50,000 (of 56,700 available in dataset)
- Verify subset: 1,791 traces (3.6%)
- Self-correction method: regex marker detection on CoT text
- Classification method: keyword-weighted scoring across 5 skill axes
- Pattern extraction: CoT structure + tool usage + behavioral signatures
- Previous version: 20K traces (v2.0.0)
- Pipeline version: 0.1.0
