---
name: fable-debug
description: Debug like Fable 5 — Root-cause analysis and fix — hypothesis-driven, systematic, and verification-focused. Distilled from 4450 real Fable 5 traces (190 debug-skill traces) with data-driven precision.
version: 3.0.0
generated_from: analysis/patterns/debug_patterns.yaml
---

# /fable-debug

Debug like Fable 5 — Root-cause analysis and fix — hypothesis-driven, systematic, and verification-focused.

## When To Use

Use this skill when debugging — crashes, silent failures, wrong output, edge-case bugs.

## Statistics & Data Provenance

This skill is empirically derived from **4450 Fable 5 traces** (Crownelius/Complete-FABLE.5-traces-2M dataset). The debug-skill subset contains **190 traces** (4.3% of total). Downloading the full 2M-trace dataset and re-running the analysis pipeline will update these numbers automatically.

| Metric | Value |
|--------|-------|
| Traces analyzed | 190 |
| Distribution | 4.3% |
| Avg classification confidence | 44.3% |
| CoT present rate | 100.0% |
| Avg CoT tokens | 402.9 |
| Median CoT tokens | 374.0 |
| Avg paragraphs | 7.2 |
| Avg sentences | 16.9 |
| Self-correction rate | 99.5% |
| Avg self-corrections | 6.92 |
| Hypothesis-driven rate | 36.3% |
| Reasoning connectors/turn | 2.19 |
| Same-turn fix rate | 19.5% |

## Core Principle

Fable 5 reasons in natural, flowing paragraphs. The debug skill is characterized by:

- **Voice**: Third-person dominant (**First-person**: 35.0%, **Second-person**: 2.0%, **Third-person**: 63.0%)
- **CoT availability**: Always present (100.0%)
- **Self-correction**: 99.5% of traces contain corrections
- **Hypothesis-driven**: 36.3% of traces use hypothesis testing
- **Same-turn fix**: 19.5% involve mid-turn course correction
- **Connectors**: 2.19 per turn — top: thus, because, therefore, since

### Opener Words

| Opener | Frequency |
|--------|-----------|
| Alright | 47.4% |
| The | 26.3% |
| I’ve | 10.5% |
| Okay | 8.4% |
| All | 3.2% |
| I need to | 3.2% |
| I | 1.1% |

### Step Transition Matrix (Top Transitions)

| From → To | Probability |
|-----------|-------------|
| ACKNOWLEDGE → PLAN | 20.1% |
| VERIFY → PLAN | 12.3% |
| PLAN → VERIFY | 11.6% |
| PLAN → ACKNOWLEDGE | 7.0% |
| ACKNOWLEDGE → VERIFY | 6.5% |
| PLAN → EXECUTE | 5.3% |
| SCOPE → PLAN | 4.8% |
| PLAN → SCOPE | 4.3% |
| EXECUTE → PLAN | 4.3% |
| ACKNOWLEDGE → EXECUTE | 3.9% |
| VERIFY → ACKNOWLEDGE | 2.7% |
| VERIFY → EXECUTE | 2.7% |

## The Natural Debug Flow

Do NOT write formal section headers. Follow this natural reasoning flow:

### 1. ACKNOWLEDGE — Context Awareness

Start with 'Alright' or 'Alright'

- Opener 'Alright' is most frequent
- Step coverage: 84.2%
- NEVER write 'ACKNOWLEDGE:' as a header

### 2. PLAN — Approach Design

Plan your approach step by step. PLAN transitions most frequently to VERIFY and EXECUTE.

- Step coverage: 123.7%
- Use connectors: thus, because, therefore
- Consider trade-offs inline

### 3. EXECUTE — Take Action

State what you'll do, then do it.

- Step coverage: 27.9%
- EXECUTE transitions most to PLAN (iterative development)

### 4. VERIFY — Validate

After actions, verify correctness.

- Step coverage: 53.2%
- 19.5% of turns involve same-turn verification

### 5. ITERATE — Self-Correct

Self-correction is universal (99.5%) — this is normal, not a failure.

- Avg 6.92 corrections per trace
- 36.3% of traces are hypothesis-driven
- Use 'Actually' or 'However' for corrections

## Behavioral Patterns

### Pattern: Hypothesis-Driven Debugging

Debug mode forms and tests hypotheses before fixing. This is the most hypothesis-driven of all skills.

**Evidence**: 42.9% hypothesis-driven rate — highest of any skill.

### Pattern: ACKNOWLEDGE→PLAN Entry Pattern

Debug mode starts by acknowledging the problem then planning the investigation. This is the highest transition probability.

**Evidence**: ACKNOWLEDGE→PLAN at 0.26 — highest transition in debug mode.

### Pattern: Same-Turn Fix Rate (23.8%)

Nearly 1 in 4 debug traces fixes the issue within the same turn. Debug mode is action-oriented.

**Evidence**: 23.8% same-turn fix rate, tied with verify as highest.

### Pattern: Self-Correction Near-Universal

100% of debug traces contain self-correction. Debugging is inherently iterative.

**Evidence**: 100% self-correction rate; 5.76 avg corrections per trace.

### Pattern: 'Alright' Opener + Investigation

Debug mode opens with 'Alright' 66.7% of the time, then immediately starts investigating.

**Evidence**: 66.7% 'Alright' opener, followed by SCOPE (0.19) and PLAN (1.05).

### Pattern: PLAN↔EXECUTE Tight Loop

Debug mode cycles rapidly between planning and executing small investigation steps.

**Evidence**: EXECUTE→PLAN at 0.065 — tightest PLAN-EXECUTE loop among all skills.

### Pattern: First-Person Investigation Narrative

Debug uses first-person for investigation narrative ('I need to check', 'let me see').

**Evidence**: 44.4% first-person, 55.6% third-person pronouns.

### Pattern: VERIFY Completes the Loop

After executing a fix, debug mode verifies before moving on. VERIFY appears in 52.4% of traces.

**Evidence**: VERIFY 0.52 coverage; transitions: PLAN→VERIFY (0.11), ACK→VERIFY (0.11).

### Pattern: Common Openers

Frequent utterance starters: Alright, The, I’ve, Okay, All

**Frequency**: 100.0%

### Pattern: Self Correction

Frequently corrects reasoning mid-turn

**Frequency**: 99.5%

### Pattern: Hypothesis Driven Debugging

Forms and tests hypotheses before fixing

**Frequency**: 36.3%

### Pattern: Acknowledge Then Execute

Always acknowledges context before acting

**Frequency**: 84.2%

### Pattern: Reasoning Chaining

Uses connectors like thus, because, therefore

**Frequency**: 43.8%

## Key Statistics from 4450 Traces (Debug Subset)

### CoT Structure
- **Avg tokens**: 402.9 (median: 374.0)
- **Avg paragraphs**: 7.2
- **Avg sentences**: 16.9
- **Avg characters**: 2541.8
- **Max tokens**: 1072, **Min tokens**: 147

### Reasoning Style
- **Pronoun distribution**: **First-person**: 35.0%, **Second-person**: 2.0%, **Third-person**: 63.0%
- **Connectors per turn**: 2.19
- **Top connectors**: thus, because, therefore, since, given that
- **Self-corrections per trace**: 6.92

### Behavior
- **Hypothesis-driven**: 36.3%
- **Multi-investigation rate**: 0.0%
- **Same-turn fix rate**: 19.5%
- **Step coverage**: ACK 84.2%, SCOPE 23.7%, GATHER 4.2%, PLAN 123.7%, EXECUTE 27.9%, VERIFY 53.2%

## Anti-Patterns

- ❌ Formal section headers (## ACKNOWLEDGE, ## SCOPE, etc.) — Fable 5 never uses them
- ❌ Using 'Oops' for self-correction — use 'Actually' or 'However' instead
- ❌ Making changes without understanding context first
- ❌ Skipping verification after changes
- ❌ Planning once without iterative refinement
- ❌ Expressing certainty when hedging is appropriate
- ❌ Writing one-sentence reasoning before deciding
