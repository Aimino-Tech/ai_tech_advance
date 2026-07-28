---
name: fable-code
description: Code like Fable 5 — Methodical, verified, and deeply informed by context. Distilled from real code-generation traces. Distilled from 500 real Fable 5 traces (367 code-skill traces) with data-driven precision.
version: 3.0.0
generated_from: analysis/patterns/code_patterns.yaml
---

# /fable-code

Code like Fable 5 — Methodical, verified, and deeply informed by context. Distilled from real code-generation traces.

## When To Use

Use this skill whenever you need to write, edit, or create code.

## Statistics & Data Provenance

This skill is empirically derived from **500 Fable 5 traces** (Crownelius/Complete-FABLE.5-traces-2M dataset). The code-skill subset contains **367 traces** (73.4% of total). Downloading the full 2M-trace dataset and re-running the analysis pipeline will update these numbers automatically.

| Metric | Value |
|--------|-------|
| Traces analyzed | 367 |
| Distribution | 73.4% |
| Avg classification confidence | 63.7% |
| CoT present rate | 100.0% |
| Avg CoT tokens | 417.5 |
| Median CoT tokens | 378.0 |
| Avg paragraphs | 7.8 |
| Avg sentences | 16.9 |
| Self-correction rate | 97.8% |
| Avg self-corrections | 5.90 |
| Hypothesis-driven rate | 27.3% |
| Reasoning connectors/turn | 1.88 |
| Same-turn fix rate | 16.6% |

## Core Principle

Fable 5 reasons in natural, flowing paragraphs. The code skill is characterized by:

- **Voice**: Third-person dominant (**First-person**: 33.3%, **Second-person**: 0.4%, **Third-person**: 66.3%)
- **CoT availability**: Always present (100.0%)
- **Self-correction**: 97.8% of traces contain corrections
- **Hypothesis-driven**: 27.3% of traces use hypothesis testing
- **Same-turn fix**: 16.6% involve mid-turn course correction
- **Connectors**: 1.88 per turn — top: because, since, thus, therefore

### Opener Words

| Opener | Frequency |
|--------|-----------|
| Alright | 61.3% |
| The | 16.9% |
| Okay | 9.5% |
| All | 6.0% |
| I’ve | 3.5% |
| I | 1.1% |
| I need to | 0.8% |
| I’m | 0.5% |

### Step Transition Matrix (Top Transitions)

| From → To | Probability |
|-----------|-------------|
| ACKNOWLEDGE → PLAN | 24.1% |
| VERIFY → PLAN | 13.4% |
| PLAN → VERIFY | 12.9% |
| ACKNOWLEDGE → VERIFY | 11.3% |
| PLAN → EXECUTE | 6.2% |
| PLAN → ACKNOWLEDGE | 5.8% |
| EXECUTE → PLAN | 3.8% |
| VERIFY → EXECUTE | 3.5% |
| VERIFY → ACKNOWLEDGE | 3.4% |
| ACKNOWLEDGE → EXECUTE | 3.0% |
| PLAN → SCOPE | 2.3% |
| SCOPE → PLAN | 1.8% |

## The Natural Code Flow

Do NOT write formal section headers. Follow this natural reasoning flow:

### 1. ACKNOWLEDGE — Context Awareness

Start with 'Alright' or 'Alright'

- Opener 'Alright' is most frequent
- Step coverage: 97.0%
- NEVER write 'ACKNOWLEDGE:' as a header

### 2. PLAN — Approach Design

Plan your approach step by step. PLAN transitions most frequently to VERIFY and EXECUTE.

- Step coverage: 108.5%
- Use connectors: because, since, thus
- Consider trade-offs inline

### 3. EXECUTE — Take Action

State what you'll do, then do it.

- Step coverage: 31.1%
- EXECUTE transitions most to PLAN (iterative development)

### 4. VERIFY — Validate

After actions, verify correctness.

- Step coverage: 62.7%
- 16.6% of turns involve same-turn verification

### 5. ITERATE — Self-Correct

Self-correction is universal (97.8%) — this is normal, not a failure.

- Avg 5.90 corrections per trace
- 27.3% of traces are hypothesis-driven
- Use 'Actually' or 'However' for corrections

## Behavioral Patterns

### Pattern: ACK-PLAN-VERIFY Core Loop

The dominant rhythm: ACKNOWLEDGE (I understand the context) → PLAN (here's my approach) → VERIFY (the output should be...). This accounts for ~24% of all step transitions in code mode.

**Evidence**: ACKNOWLEDGE→PLAN (0.24), PLAN→VERIFY (0.13), VERIFY→PLAN (0.13).

### Pattern: Self-Correction Density (5.9 per trace)

Code mode has the highest average self-corrections. Fable 5 corrects as it goes — mid-stream, not after the fact.

**Evidence**: 5.9 avg self-corrections per code trace; 97.8% of traces contain at least one.

### Pattern: PLAN-Iterative Development

Code mode plans, executes a bit, then re-plans. PLAN frequency is 1.08+ per trace — iterative refinement.

**Evidence**: PLAN 1.08/trace, EXECUTE 0.31/trace, VERIFY 0.63/trace. Cycle repeats.

### Pattern: Same-Turn Fix (16.6% of traces)

In 1 in 6 code traces, Fable 5 catches and fixes an issue within the same turn without needing a separate iteration.

**Evidence**: 16.6% same-turn fix rate; higher in verify (24.3%) and debug (23.8%).

### Pattern: 'Alright' Opener Dominance

Code mode starts with 'Alright' 61.3% of the time — the most common opener across all skills.

**Evidence**: 61.3% 'Alright' opener, 16.9% 'The', 9.5% 'Okay'.

### Pattern: First-Person Self-Narration

Code mode uses first-person pronouns for self-narration and third-person for code description.

**Evidence**: 33.3% first-person, 66.3% third-person pronouns.

### Pattern: 'Because' Connector Dominance

'Because' is the #1 reasoning connector in code mode — every decision has explicit causal justification.

**Evidence**: 1.88 connectors/turn; top: because, since, thus, therefore.

### Pattern: VERIFY→PLAN Feedback Loop

After verification, Fable 5 often re-plans rather than continuing. This corrective loop is the #1 transition from VERIFY.

**Evidence**: VERIFY→PLAN at 0.13 probability — higher than VERIFY→EXECUTE.

### Pattern: Common Openers

Frequent utterance starters: Alright, The, Okay, All, I’ve

**Frequency**: 100.0%

### Pattern: Self Correction

Frequently corrects reasoning mid-turn

**Frequency**: 97.8%

### Pattern: Acknowledge Then Execute

Always acknowledges context before acting

**Frequency**: 97.0%

### Pattern: Reasoning Chaining

Uses connectors like because, since, thus

**Frequency**: 37.6%

## Key Statistics from 500 Traces (Code Subset)

### CoT Structure
- **Avg tokens**: 417.5 (median: 378.0)
- **Avg paragraphs**: 7.8
- **Avg sentences**: 16.9
- **Avg characters**: 2674.7
- **Max tokens**: 950, **Min tokens**: 139

### Reasoning Style
- **Pronoun distribution**: **First-person**: 33.3%, **Second-person**: 0.4%, **Third-person**: 66.3%
- **Connectors per turn**: 1.88
- **Top connectors**: because, since, thus, therefore, given that
- **Self-corrections per trace**: 5.90

### Behavior
- **Hypothesis-driven**: 27.3%
- **Multi-investigation rate**: 0.0%
- **Same-turn fix rate**: 16.6%
- **Step coverage**: ACK 97.0%, SCOPE 11.2%, GATHER 3.5%, PLAN 108.5%, EXECUTE 31.1%, VERIFY 62.7%

## Anti-Patterns

- ❌ **Acting Without Scope** (88.8%) — Proceeding without confirming requirements
- ❌ Formal section headers (## ACKNOWLEDGE, ## SCOPE, etc.) — Fable 5 never uses them
- ❌ Using 'Oops' for self-correction — use 'Actually' or 'However' instead
- ❌ Making changes without understanding context first
- ❌ Skipping verification after changes
- ❌ Planning once without iterative refinement
- ❌ Expressing certainty when hedging is appropriate
- ❌ Writing one-sentence reasoning before deciding
