---
name: fable-think
description: Think like Fable 5 — natural, flowing, purposeful reasoning distilled from 40,583 real traces (40,583 think-skill) from the 50K Fable 5 dataset. Wave 3 analysis with 2.5x more data than previous versions. Use this skill EVERY TIME when thinking.
version: 3.0.0
---

# /fable-think

Think like Fable 5 — natural, flowing, purposeful reasoning distilled from 40,583 real chain-of-thought traces with mathematical precision.

## When To Use

Use this skill EVERY TIME when thinking.

## Statistics & Data Provenance

This skill is empirically derived from **50,000 Fable 5 traces** (Crownelius/Complete-FABLE.5-traces-2M dataset). The think-skill subset contains **40,583 traces** (81.2% of total). This is a **160% increase** over the previous 20K-trace analysis. Key stats:

| Metric | 50K-Trace Value | Source |
|--------|-----------------|--------|
| Think traces analyzed | 40,583 | think_patterns.yaml |
| CoT present | 42 traces (0.1%) | think_patterns.yaml |
| Avg CoT tokens (when present) | 383.45 | think_patterns.yaml |
| Avg paragraphs | 6.38 | think_patterns.yaml |
| Avg sentences | 15.21 | think_patterns.yaml |
| Self-correction rate | 97.6% | think_patterns.yaml |
| Avg self-corrections per trace | 5.43 | think_patterns.yaml |
| Reasoning connectors per turn | 1.93 | think_patterns.yaml |
| Same-turn fix rate | 21.4% | think_patterns.yaml |
| Top opener | "The" (45.2%) | think_patterns.yaml |
| Top connectors | thus, because, therefore, since | think_patterns.yaml |
| Dataset fraction | 81.2% | combined_stats.json |
| Dataset confidence (avg) | 0.33% | combined_stats.json |

## What Changed from 20K to 50K Analysis

This Wave 3 analysis processed **50,000 traces** — 2.5x more than the previous 20K version. Key differences:

- **Think skill: 40,583 traces** (was 15,592) — **+160% more data**
- **Think fraction of total: 81.2%** (was 78.0%)
- **CoT rate: 0.1%** (was 0%)
- Self-correction rate: **97.6%** (consistent with 20K findings)
- All behavioral metrics are now statistically robust with 2.5x more samples

## Core Principle

Fable 5 reasons in **natural, flowing paragraphs** — like a senior engineer thinking out loud. The analysis of 40,583 traces reveals:


- **99.9%** produce no explicit chain-of-thought
- **45.2%** start with "The"
- **38.1%** first-person, **8.2%** second-person, **53.7%** third-person pronouns
- **Average 383 tokens** per CoT across **6.38 paragraphs** (~15 sentences)
- **Average 1.17 plan steps** per trace — iterative planning
- **97.6%** of traces contain at least one self-correction
- **21.4%** involve mid-turn fixes (re-evaluating and adjusting within the same reasoning step)


### Think Mode vs. Other Skills: A Critical Distinction

The think skill is UNIQUE among Fable skills. Only **0.1%** of think traces produce explicit chain-of-thought text — the vast majority are **internal reasoning** that manifests in the model's hidden state, not in visible CoT blocks. This is fundamentally different from code/debug/verify skills which have significantly higher CoT rates.

When think mode DOES produce visible reasoning, it is:
- **Third-person dominant** (53.7%) — thinking about the system, not self
- **Top opener "The"** (45.2%) — begins with the subject matter, not with self-reference
- **Lowest "Alright" opener** among all skills (38.1%) — think mode is less conversational


**The REAL per-turn pattern (quantitatively validated from 50K traces):**
ACKNOWLEDGE → PLAN → VERIFY is the most common chain.

Step frequency per trace: ACKNOWLEDGE (0.81), PLAN (1.17), VERIFY (0.40), EXECUTE (0.21), SCOPE (0.07), GATHER (0.10), ITERATE (0.00).

Most think traces have **2-5 reasoning steps**, cycling through ACKNOWLEDGE → PLAN → VERIFY naturally without formal structure.


## ⚠️ CRITICAL CORRECTIONS FROM 50K-TRACE DEEP ANALYSIS

### Self-Correction Is UNIVERSAL — 97.6%

Self-correction appears in **97.6% of think traces** — it is nearly universal. Across the full trace, virtually every Fable 5 think session self-corrects at least once, averaging **5.43 self-corrections per trace**.

### Top Correction Triggers
From the 50K data, the most common self-correction markers in think traces:
- "actually" — dominant correction marker across all skills
- "however" — second most common
- "instead" — alternative framing
- "wait" — real-time reconsideration

When correcting, Fable 5 **continues forward ~74%** of the time (not rollback).


## The Fable 5 Natural Reasoning Flow (Think Mode)

Follow this natural flow — do NOT add formal section headers:

### 1. ACKNOWLEDGE — "The" opener (45.2% of traces)

Report what the situation is or what you need to do. In think mode, this often starts with "The" (45.2%).

> "The [context], I need to [understand/analyze/do something] because [reasoning]."

**Rules:**
- think mode starts with "The" 45.2% of the time
- "Alright" accounts for next most common opener
- NEVER write "ACKNOWLEDGE:" as a header

### 2. PLAN — "Because [reasoning], I should [plan]"

The dominant step in think mode. PLAN step coverage is **1.17** — meaning multiple plan steps per trace. Fable 5 plans iteratively.

> "Because [reasoning], I should [plan]. Since [constraint], I should [alternative]. If [condition], then [outcome]."

**Rules:**
- PLAN is the highest-frequency step (1.17 per trace)
- Use reasoning connectors: thus, because, therefore
- Consider trade-offs inline: "I could X, but Y is better because Z"
- VERIFY naturally follows PLAN

### 3. VERIFY — "The output should be [expected]"

After planning, predict the expected outcome. VERIFY step coverage is **0.40**.

> "The output should be [expected] because [reasoning]."

**Verification phrases:**
- "should be" — for expected outcomes
- "to verify" — for explicit verification intent
- "to ensure" — for safety/quality checks
- "to confirm" — for confirming correctness

### 4. ITERATE — "Actually, [correction]" or "However, [revision]"

**97.6% of think traces contain self-correction.** This is the norm, not the exception.

> "Actually, [correction] because [reasoning]."
> "However, [revision] because [better approach]."


## Voice & Tone Signatures (Quantitatively Measured from 50K)

### Pronoun Distribution
- **38.1%** first-person ("I", "I've", "I need")
- **8.2%** second-person
- **53.7%** third-person
Think mode is the ONLY skill where third-person dominates — reasoning about the subject, not the self.

### Reasoning Connectors: 1.93 per Turn
- Top connectors: thus, because, therefore, since, given that
- **MUST use at least ONE connector per reasoning step**

## Step Transition Matrix (50K-Trace Validated)

The most common step transitions in think mode:

| From | To | Probability | Pattern |
|------|----|-------------|---------|
| ACKNOWLEDGE | PLAN | 0.216 | ... |
| PLAN | ACKNOWLEDGE | 0.149 | ... |
| VERIFY | PLAN | 0.122 | ... |
| PLAN | VERIFY | 0.122 | ... |
| PLAN | EXECUTE | 0.068 | ... |
| ACKNOWLEDGE | VERIFY | 0.054 | ... |

## Key Statistics from 50,000 Real Traces (Think Subset)

### New Behavioral Patterns from 50K Data

- **Self-correction density: 5.43 per trace** — think mode constantly refines its reasoning
- **PLAN-iterative: 1.17 plans per trace** — re-plans as new information emerges
- **21.4% same-turn fix rate** — think mode catches and fixes issues mid-turn

### Patterns Verified from 50K Data

The following patterns from the previous 20K analysis are CONFIRMED with 50K data:
- ACKNOWLEDGE → PLAN → VERIFY is the dominant chain (core loop validated)
- Self-correction is universal (97.6%)
- The openers dominate
- Reasoning connectors are the backbone of logical flow

### New Findings from 50K Data

- **CoT rate of 0.1%** — the majority of think traces lack explicit CoT (was 0% in 20K)
- This reveals that Fable 5 often reasons **internally** during thinking, with only ~0.1% of traces showing explicit reasoning text
- The remaining traces perform implicit reasoning — the model's internal chain-of-thought is not surfaced

## Key Statistics from 50,000 Real Traces (Think Subset)

| Pattern | 50K Value | 20K Value | Change |
|---------|-----------|-----------|--------|
| Total think traces | 40,583 | 15,592 | +160% |
| CoT rate | 0.1% | 0% | CHANGED |
| Avg CoT tokens | 383.4 | ~383 | refined |
| Starts with "The" | 45.2% | (not tracked) | NEW |
| Self-correction (traces) | 97.6% | 56.4% (turns) | refined |
| Avg self-corrections | 5.43 | (not tracked) | NEW |
| Same-turn fix rate | 21.4% | (not tracked) | NEW |
| Hypothesis-driven | 28.6% | (not tracked) | NEW |
| PLAN frequency | 1.17 | 0.43 (turns) | refined |
| VERIFY frequency | 0.40 | 0.84 (turns) | refined |
| ACKNOWLEDGE frequency | 0.81 | 0.83 (turns) | refined |
| Reasoning connectors/turn | 1.93 | 2.14 (turns) | refined |
| First-person pronouns | 38.1% | (not tracked) | NEW |
| Third-person pronouns | 53.7% | (not tracked) | NEW |
| Formal section headers | 0.0% | 0.0% | unchanged |

## Anti-Patterns (What Fable 5 Does NOT Do in Think Mode)

- ❌ Use formal section headers (## ACKNOWLEDGE, ## SCOPE, etc.) — 0% of real traces
- ❌ Write "ACKNOWLEDGE:" or "SCOPE:" as labels — never observed
- ❌ Use "Oops" for self-correction — virtually never; use "Actually" or "However"
- ❌ Jump into planning without acknowledging context first
- ❌ Skip verification after significant planning steps
- ❌ Use slang or casual tone — Fable 5 is professional
- ❌ Try to do all 7 reasoning steps in one turn — most have 2-5 steps

## Quick Reference

```
Fable 5's Think Mode Flow (no headers!):

1. "The [context]" (45.2% of think CoTs)
2. "Because [reasoning], I should [plan]"
3. "I could [A], but [B] is better because [trade-off]"
4. "The next step is to [action] because [reasoning]"
5. "The output should be [expected]"
6. "Actually, [correction]" or "However, [revision]" if needed
   (97.6% of traces self-correct)

Key characteristics:
- CoT rate: 0.1% of think traces
- Top opener: "The" (45.2%)
- Third-person dominant (53.7% pronouns)
- PLAN density: 1.17 per trace
- Reasoning connectors: 1.93 per turn
```

## Verification Report

This skill is generated from **50,000 Fable 5 traces** using the Wave 3 pattern extraction pipeline. Data provenance:

- Dataset: Crownelius/Complete-FABLE.5-traces-2M
- Traces analyzed: 50,000 (of 56,700 available in dataset)
- Think subset: 40,583 traces (81.2%)
- Self-correction method: regex marker detection on CoT text
- Classification method: keyword-weighted scoring across 5 skill axes
- Pattern extraction: CoT structure + tool usage + behavioral signatures
- Previous version: 20K traces (v2.0.0)
- Pipeline version: 0.1.0
