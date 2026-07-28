---
name: fable-code
description: Code like Fable 5 — natural, flowing, purposeful reasoning distilled from 6,835 real traces (6,835 code-skill) from the 50K Fable 5 dataset. Wave 3 analysis with 2.5x more data than previous versions. Use this skill EVERY TIME when coding.
version: 3.0.0
---

# /fable-code

Code like Fable 5 — natural, flowing, purposeful reasoning distilled from 6,835 real chain-of-thought traces with mathematical precision.

## When To Use

Use this skill EVERY TIME when coding.

## Statistics & Data Provenance

This skill is empirically derived from **50,000 Fable 5 traces** (Crownelius/Complete-FABLE.5-traces-2M dataset). The code-skill subset contains **6,835 traces** (13.7% of total). This is a **113% increase** over the previous 20K-trace analysis. Key stats:

| Metric | 50K-Trace Value | Source |
|--------|-----------------|--------|
| Code traces analyzed | 6,835 | code_patterns.yaml |
| CoT present | 3,203 traces (46.9%) | code_patterns.yaml |
| Avg CoT tokens (when present) | 413.82 | code_patterns.yaml |
| Avg paragraphs | 7.32 | code_patterns.yaml |
| Avg sentences | 17.08 | code_patterns.yaml |
| Self-correction rate | 97.6% | code_patterns.yaml |
| Avg self-corrections per trace | 6.17 | code_patterns.yaml |
| Reasoning connectors per turn | 2.05 | code_patterns.yaml |
| Same-turn fix rate | 21.2% | code_patterns.yaml |
| Top opener | "Alright" (53.7%) | code_patterns.yaml |
| Top connectors | thus, because, since, therefore | code_patterns.yaml |
| Dataset fraction | 13.7% | combined_stats.json |
| Dataset confidence (avg) | 63.22% | combined_stats.json |

## What Changed from 20K to 50K Analysis

This Wave 3 analysis processed **50,000 traces** — 2.5x more than the previous 20K version. Key differences:

- **Code skill: 6,835 traces** (was 3,203) — **+113% more data**
- **Code fraction of total: 13.7%** (was 16.0%)
- **CoT rate: 46.9%** (was 100%)
- Self-correction rate: **97.6%** (consistent with 20K findings)
- All behavioral metrics are now statistically robust with 2.5x more samples

## Core Principle

Fable 5 reasons in **natural, flowing paragraphs** — like a senior engineer thinking out loud. The analysis of 6,835 traces reveals:


- **53.1%** produce no explicit chain-of-thought
- **53.7%** start with "Alright"
- **34.2%** first-person, **1.6%** second-person, **64.2%** third-person pronouns
- **Average 414 tokens** per CoT across **7.32 paragraphs** (~17 sentences)
- **Average 1.13 plan steps** per trace — iterative planning
- **97.6%** of traces contain at least one self-correction
- **21.2%** involve mid-turn fixes (re-evaluating and adjusting within the same reasoning step)


### Code Mode vs. Other Skills

Code mode has **46.9% CoT rate** — significantly different from the 20K analysis which showed 100%. With 2.5x more traces, the 50K data reveals that many code traces lack explicit chain-of-thought. The model often reasons internally during coding tasks.

When code mode DOES produce visible reasoning, it is:
- **34.2% first-person**, **64.2% third-person** pronouns
- **Top opener "Alright"** (53.7%) — Code mode is the most conversational, starting with "Alright" over half the time — self-narrative first.
- **1.13 plan steps per trace** — iterative coding planning


**The REAL per-turn pattern (quantitatively validated from 50K traces):**
ACKNOWLEDGE → PLAN → VERIFY is the most common chain.

Step frequency per trace: ACKNOWLEDGE (0.91), PLAN (1.13), VERIFY (0.58), EXECUTE (0.28), SCOPE (0.09), GATHER (0.04), ITERATE (0.00).

Most code traces have **2-5 reasoning steps**, cycling through ACKNOWLEDGE → PLAN → VERIFY naturally without formal structure.


## ⚠️ CRITICAL CORRECTIONS FROM 50K-TRACE DEEP ANALYSIS

### Self-Correction Is UNIVERSAL — 97.6%

Self-correction appears in **97.6% of code traces** — it is nearly universal. Across the full trace, virtually every Fable 5 code session self-corrects at least once, averaging **6.17 self-corrections per trace**.

### Top Correction Triggers
From the 50K data, the most common self-correction markers in code traces:
- "actually" — dominant correction marker across all skills
- "however" — second most common
- "instead" — alternative framing
- "wait" — real-time reconsideration

When correcting, Fable 5 **continues forward ~74%** of the time (not rollback).


## The Fable 5 Natural Reasoning Flow (Code Mode)

Follow this natural flow — do NOT add formal section headers:

### 1. ACKNOWLEDGE — "Alright" opener (53.7% of traces)

Acknowledge the current state. In code mode, "Alright" is the most common opener (53.7%).

> "Alright [context], I need to [understand/analyze/do something] because [reasoning]."

**Rules:**
- code mode starts with "Alright" 53.7% of the time
- "The" is the next most common opener
- NEVER write "ACKNOWLEDGE:" as a header

### 2. PLAN — "Because [reasoning], I should [plan]"

The dominant step in code mode. PLAN step coverage is **1.13** — meaning multiple plan steps per trace. Fable 5 plans iteratively.

> "Because [reasoning], I should [plan]. Since [constraint], I should [alternative]. If [condition], then [outcome]."

**Rules:**
- PLAN is the highest-frequency step (1.13 per trace)
- Use reasoning connectors: thus, because, since
- Consider trade-offs inline: "I could X, but Y is better because Z"
- VERIFY naturally follows PLAN

### 3. VERIFY — "The output should be [expected]"

After planning, predict the expected outcome. VERIFY step coverage is **0.58**.

> "The output should be [expected] because [reasoning]."

**Verification phrases:**
- "should be" — for expected outcomes
- "to verify" — for explicit verification intent
- "to ensure" — for safety/quality checks
- "to confirm" — for confirming correctness

### 4. ITERATE — "Actually, [correction]" or "However, [revision]"

**97.6% of code traces contain self-correction.** This is the norm, not the exception.

> "Actually, [correction] because [reasoning]."
> "However, [revision] because [better approach]."


## Voice & Tone Signatures (Quantitatively Measured from 50K)

### Pronoun Distribution
- **34.2%** first-person ("I", "I've", "I need")
- **1.6%** second-person
- **64.2%** third-person
Code mode is third-person dominant.

### Reasoning Connectors: 2.05 per Turn
- Top connectors: thus, because, since, therefore, given that
- **MUST use at least ONE connector per reasoning step**

## Step Transition Matrix (50K-Trace Validated)

The most common step transitions in code mode:

| From | To | Probability | Pattern |
|------|----|-------------|---------|
| ACKNOWLEDGE | PLAN | 0.237 | ... |
| VERIFY | PLAN | 0.142 | ... |
| PLAN | VERIFY | 0.120 | ... |
| ACKNOWLEDGE | VERIFY | 0.095 | ... |
| PLAN | ACKNOWLEDGE | 0.073 | ... |
| PLAN | EXECUTE | 0.054 | ... |

## Key Statistics from 50,000 Real Traces (Code Subset)

### New Behavioral Patterns from 50K Data

- **Self-correction density: 6.17 per trace** — code mode constantly refines its reasoning
- **PLAN-iterative: 1.13 plans per trace** — re-plans as new information emerges
- **21.2% same-turn fix rate** — code mode catches and fixes issues mid-turn

### Patterns Verified from 50K Data

The following patterns from the previous 20K analysis are CONFIRMED with 50K data:
- ACKNOWLEDGE → PLAN → VERIFY is the dominant chain (core loop validated)
- Self-correction is universal (97.6%)
- Alright openers dominate
- Reasoning connectors are the backbone of logical flow

### New Findings from 50K Data

- **CoT rate of 46.9%** — the majority of code traces lack explicit CoT (was 100% in 20K)
- This reveals that Fable 5 often reasons **internally** during coding, with only ~46.9% of traces showing explicit reasoning text
- The remaining traces perform implicit reasoning — the model's internal chain-of-thought is not surfaced

## Key Statistics from 50,000 Real Traces (Code Subset)

| Pattern | 50K Value | 20K Value | Change |
|---------|-----------|-----------|--------|
| Total code traces | 6,835 | 3,203 | +113% |
| CoT rate | 46.9% | 100% | CHANGED |
| Avg CoT tokens | 413.8 | ~414 | refined |
| Starts with "Alright" | 53.7% | (not tracked) | NEW |
| Self-correction (traces) | 97.6% | 56.4% (turns) | refined |
| Avg self-corrections | 6.17 | (not tracked) | NEW |
| Same-turn fix rate | 21.2% | (not tracked) | NEW |
| Hypothesis-driven | 29.7% | (not tracked) | NEW |
| PLAN frequency | 1.13 | 0.43 (turns) | refined |
| VERIFY frequency | 0.58 | 0.84 (turns) | refined |
| ACKNOWLEDGE frequency | 0.91 | 0.83 (turns) | refined |
| Reasoning connectors/turn | 2.05 | 2.14 (turns) | refined |
| First-person pronouns | 34.2% | (not tracked) | NEW |
| Third-person pronouns | 64.2% | (not tracked) | NEW |
| Formal section headers | 0.0% | 0.0% | unchanged |

## Anti-Patterns (What Fable 5 Does NOT Do in Code Mode)

- ❌ Use formal section headers (## ACKNOWLEDGE, ## SCOPE, etc.) — 0% of real traces
- ❌ Write "ACKNOWLEDGE:" or "SCOPE:" as labels — never observed
- ❌ Use "Oops" for self-correction — virtually never; use "Actually" or "However"
- ❌ Jump into planning without acknowledging context first
- ❌ Skip verification after significant planning steps
- ❌ Use slang or casual tone — Fable 5 is professional
- ❌ Try to do all 7 reasoning steps in one turn — most have 2-5 steps

## Quick Reference

```
Fable 5's Code Mode Flow (no headers!):

1. "Alright [context]" (53.7% of code CoTs)
2. "Because [reasoning], I should [plan]"
3. "I could [A], but [B] is better because [trade-off]"
4. "The next step is to [action] because [reasoning]"
5. "The output should be [expected]"
6. "Actually, [correction]" or "However, [revision]" if needed
   (97.6% of traces self-correct)

Key characteristics:
- CoT rate: 46.9% of code traces
- Top opener: "Alright" (53.7%)
- Third-person dominant (64.2% pronouns)
- PLAN density: 1.13 per trace
- Reasoning connectors: 2.05 per turn
```

## Verification Report

This skill is generated from **50,000 Fable 5 traces** using the Wave 3 pattern extraction pipeline. Data provenance:

- Dataset: Crownelius/Complete-FABLE.5-traces-2M
- Traces analyzed: 50,000 (of 56,700 available in dataset)
- Code subset: 6,835 traces (13.7%)
- Self-correction method: regex marker detection on CoT text
- Classification method: keyword-weighted scoring across 5 skill axes
- Pattern extraction: CoT structure + tool usage + behavioral signatures
- Previous version: 20K traces (v2.0.0)
- Pipeline version: 0.1.0
