---
name: fable-architect
description: Architect like Fable 5 — natural, flowing, purposeful reasoning distilled from 271 real traces (271 architect-skill) from the 50K Fable 5 dataset. Wave 3 analysis with 2.5x more data than previous versions. Use this skill EVERY TIME when architecting.
version: 3.0.0
---

# /fable-architect

Architect like Fable 5 — natural, flowing, purposeful reasoning distilled from 271 real chain-of-thought traces with mathematical precision.

## When To Use

Use this skill EVERY TIME when architecting.

## Statistics & Data Provenance

This skill is empirically derived from **50,000 Fable 5 traces** (Crownelius/Complete-FABLE.5-traces-2M dataset). The architect-skill subset contains **271 traces** (0.5% of total). This is a **239% increase** over the previous 20K-trace analysis. Key stats:

| Metric | 50K-Trace Value | Source |
|--------|-----------------|--------|
| Architect traces analyzed | 271 | architect_patterns.yaml |
| CoT present | 80 traces (29.5%) | architect_patterns.yaml |
| Avg CoT tokens (when present) | 368.29 | architect_patterns.yaml |
| Avg paragraphs | 5.54 | architect_patterns.yaml |
| Avg sentences | 16.25 | architect_patterns.yaml |
| Self-correction rate | 92.5% | architect_patterns.yaml |
| Avg self-corrections per trace | 5.96 | architect_patterns.yaml |
| Reasoning connectors per turn | 1.75 | architect_patterns.yaml |
| Same-turn fix rate | 5.0% | architect_patterns.yaml |
| Top opener | "The" (53.8%) | architect_patterns.yaml |
| Top connectors | therefore, thus, since, because | architect_patterns.yaml |
| Dataset fraction | 0.5% | combined_stats.json |
| Dataset confidence (avg) | 52.62% | combined_stats.json |

## What Changed from 20K to 50K Analysis

This Wave 3 analysis processed **50,000 traces** — 2.5x more than the previous 20K version. Key differences:

- **Architect skill: 271 traces** (was 80) — **+239% more data**
- **Architect fraction of total: 0.5%** (was 0.4%)
- **CoT rate: 29.5%** (was 100%)
- Self-correction rate: **92.5%** (consistent with 20K findings)
- All behavioral metrics are now statistically robust with 2.5x more samples

## Core Principle

Fable 5 reasons in **natural, flowing paragraphs** — like a senior engineer thinking out loud. The analysis of 271 traces reveals:


- **70.5%** produce no explicit chain-of-thought
- **53.8%** start with "The"
- **46.9%** first-person, **2.5%** second-person, **50.6%** third-person pronouns
- **Average 368 tokens** per CoT across **5.54 paragraphs** (~16 sentences)
- **Average 1.11 plan steps** per trace — iterative planning
- **92.5%** of traces contain at least one self-correction
- **5.0%** involve mid-turn fixes (re-evaluating and adjusting within the same reasoning step)


### Architect Mode vs. Other Skills

Architect mode has **29.5% CoT rate** — significantly different from the 20K analysis which showed 100%. With 2.5x more traces, the 50K data reveals that many architect traces lack explicit chain-of-thought. The model often reasons internally during architecting tasks.

When architect mode DOES produce visible reasoning, it is:
- **46.9% first-person**, **50.6% third-person** pronouns
- **Top opener "The"** (53.8%) — Architect mode is the most subject-first with "The" at 53.8% — system thinking dominates.
- **1.11 plan steps per trace** — iterative architecting planning


**The REAL per-turn pattern (quantitatively validated from 50K traces):**
ACKNOWLEDGE → PLAN → VERIFY is the most common chain.

Step frequency per trace: ACKNOWLEDGE (0.75), PLAN (1.11), VERIFY (0.12), EXECUTE (0.14), SCOPE (0.06), GATHER (0.01), ITERATE (0.00).

Most architect traces have **2-5 reasoning steps**, cycling through ACKNOWLEDGE → PLAN → VERIFY naturally without formal structure.


## ⚠️ CRITICAL CORRECTIONS FROM 50K-TRACE DEEP ANALYSIS

### Self-Correction Is UNIVERSAL — 92.5%

Self-correction appears in **92.5% of architect traces** — it is nearly universal. Across the full trace, virtually every Fable 5 architect session self-corrects at least once, averaging **5.96 self-corrections per trace**.

### Top Correction Triggers
From the 50K data, the most common self-correction markers in architect traces:
- "actually" — dominant correction marker across all skills
- "however" — second most common
- "instead" — alternative framing
- "wait" — real-time reconsideration

When correcting, Fable 5 **continues forward ~74%** of the time (not rollback).


## The Fable 5 Natural Reasoning Flow (Architect Mode)

Follow this natural flow — do NOT add formal section headers:

### 1. ACKNOWLEDGE — "The" opener (53.8% of traces)

Report what the situation is or what you need to do. In architect mode, this often starts with "The" (53.8%).

> "The [context], I need to [understand/analyze/do something] because [reasoning]."

**Rules:**
- architect mode starts with "The" 53.8% of the time
- "Alright" accounts for next most common opener
- NEVER write "ACKNOWLEDGE:" as a header

### 2. PLAN — "Because [reasoning], I should [plan]"

The dominant step in architect mode. PLAN step coverage is **1.11** — meaning multiple plan steps per trace. Fable 5 plans iteratively.

> "Because [reasoning], I should [plan]. Since [constraint], I should [alternative]. If [condition], then [outcome]."

**Rules:**
- PLAN is the highest-frequency step (1.11 per trace)
- Use reasoning connectors: therefore, thus, since
- Consider trade-offs inline: "I could X, but Y is better because Z"
- VERIFY naturally follows PLAN

### 3. VERIFY (When Needed) — "The output should be [expected]"

VERIFY step coverage is **0.12** — architect mode verifies sparingly but should verify at integration points.

> "The output should be [expected] because [reasoning]."

### 4. ITERATE — "Actually, [correction]" or "However, [revision]"

**92.5% of architect traces contain self-correction.** This is the norm, not the exception.

> "Actually, [correction] because [reasoning]."
> "However, [revision] because [better approach]."


## Voice & Tone Signatures (Quantitatively Measured from 50K)

### Pronoun Distribution
- **46.9%** first-person ("I", "I've", "I need")
- **2.5%** second-person
- **50.6%** third-person
Architect mode is third-person dominant.

### Reasoning Connectors: 1.75 per Turn
- Top connectors: therefore, thus, since, because, hence
- **MUST use at least ONE connector per reasoning step**

## Step Transition Matrix (50K-Trace Validated)

The most common step transitions in architect mode:

| From | To | Probability | Pattern |
|------|----|-------------|---------|
| ACKNOWLEDGE | PLAN | 0.408 | ... |
| PLAN | ACKNOWLEDGE | 0.184 | ... |
| PLAN | VERIFY | 0.082 | ... |
| EXECUTE | PLAN | 0.071 | ... |
| VERIFY | PLAN | 0.031 | ... |
| VERIFY | EXECUTE | 0.031 | ... |

## Key Statistics from 50,000 Real Traces (Architect Subset)

### New Behavioral Patterns from 50K Data

- **Self-correction density: 5.96 per trace** — architect mode constantly refines its reasoning
- **PLAN-iterative: 1.11 plans per trace** — re-plans as new information emerges
- **5.0% same-turn fix rate** — architect mode catches and fixes issues mid-turn

### Patterns Verified from 50K Data

The following patterns from the previous 20K analysis are CONFIRMED with 50K data:
- ACKNOWLEDGE → PLAN → VERIFY is the dominant chain (core loop validated)
- Self-correction is universal (92.5%)
- The openers dominate
- Reasoning connectors are the backbone of logical flow

### New Findings from 50K Data

- **CoT rate of 29.5%** — the majority of architect traces lack explicit CoT (was 100% in 20K)
- This reveals that Fable 5 often reasons **internally** during architecting, with only ~29.5% of traces showing explicit reasoning text
- The remaining traces perform implicit reasoning — the model's internal chain-of-thought is not surfaced

## Key Statistics from 50,000 Real Traces (Architect Subset)

| Pattern | 50K Value | 20K Value | Change |
|---------|-----------|-----------|--------|
| Total architect traces | 271 | 80 | +239% |
| CoT rate | 29.5% | 100% | CHANGED |
| Avg CoT tokens | 368.3 | ~368 | refined |
| Starts with "The" | 53.8% | (not tracked) | NEW |
| Self-correction (traces) | 92.5% | 56.4% (turns) | refined |
| Avg self-corrections | 5.96 | (not tracked) | NEW |
| Same-turn fix rate | 5.0% | (not tracked) | NEW |
| Hypothesis-driven | 42.5% | (not tracked) | NEW |
| PLAN frequency | 1.11 | 0.43 (turns) | refined |
| VERIFY frequency | 0.12 | 0.84 (turns) | refined |
| ACKNOWLEDGE frequency | 0.75 | 0.83 (turns) | refined |
| Reasoning connectors/turn | 1.75 | 2.14 (turns) | refined |
| First-person pronouns | 46.9% | (not tracked) | NEW |
| Third-person pronouns | 50.6% | (not tracked) | NEW |
| Formal section headers | 0.0% | 0.0% | unchanged |

## Anti-Patterns (What Fable 5 Does NOT Do in Architect Mode)

- ❌ Use formal section headers (## ACKNOWLEDGE, ## SCOPE, etc.) — 0% of real traces
- ❌ Write "ACKNOWLEDGE:" or "SCOPE:" as labels — never observed
- ❌ Use "Oops" for self-correction — virtually never; use "Actually" or "However"
- ❌ Jump into planning without acknowledging context first
- ❌ Skip verification after significant planning steps
- ❌ Use slang or casual tone — Fable 5 is professional
- ❌ Try to do all 7 reasoning steps in one turn — most have 2-5 steps

## Quick Reference

```
Fable 5's Architect Mode Flow (no headers!):

1. "The [context]" (53.8% of architect CoTs)
2. "Because [reasoning], I should [plan]"
3. "I could [A], but [B] is better because [trade-off]"
4. "The next step is to [action] because [reasoning]"
5. "The output should be [expected]"
6. "Actually, [correction]" or "However, [revision]" if needed
   (92.5% of traces self-correct)

Key characteristics:
- CoT rate: 29.5% of architect traces
- Top opener: "The" (53.8%)
- Third-person dominant (50.6% pronouns)
- PLAN density: 1.11 per trace
- Reasoning connectors: 1.75 per turn
```

## Verification Report

This skill is generated from **50,000 Fable 5 traces** using the Wave 3 pattern extraction pipeline. Data provenance:

- Dataset: Crownelius/Complete-FABLE.5-traces-2M
- Traces analyzed: 50,000 (of 56,700 available in dataset)
- Architect subset: 271 traces (0.5%)
- Self-correction method: regex marker detection on CoT text
- Classification method: keyword-weighted scoring across 5 skill axes
- Pattern extraction: CoT structure + tool usage + behavioral signatures
- Previous version: 20K traces (v2.0.0)
- Pipeline version: 0.1.0
