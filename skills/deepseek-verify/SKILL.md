---
name: fable-verify
description: Verify like Fable 5 — Self-verification and test generation — thorough validation before declaring done. Distilled from 500 real Fable 5 traces (103 verify-skill traces) with data-driven precision.
version: 3.0.0
generated_from: analysis/patterns/verify_patterns.yaml
---

# /fable-verify

Verify like Fable 5 — Self-verification and test generation — thorough validation before declaring done.

## When To Use

Use this skill when writing tests, validating output, or reviewing code for correctness.

## Statistics & Data Provenance

This skill is empirically derived from **500 Fable 5 traces** (Crownelius/Complete-FABLE.5-traces-2M dataset). The verify-skill subset contains **103 traces** (20.6% of total). Downloading the full 2M-trace dataset and re-running the analysis pipeline will update these numbers automatically.

| Metric | Value |
|--------|-------|
| Traces analyzed | 103 |
| Distribution | 20.6% |
| Avg classification confidence | 52.0% |
| CoT present rate | 100.0% |
| Avg CoT tokens | 417.7 |
| Median CoT tokens | 390.0 |
| Avg paragraphs | 7.5 |
| Avg sentences | 16.0 |
| Self-correction rate | 100.0% |
| Avg self-corrections | 7.50 |
| Hypothesis-driven rate | 27.2% |
| Reasoning connectors/turn | 1.89 |
| Same-turn fix rate | 24.3% |

## Core Principle

Fable 5 reasons in natural, flowing paragraphs. The verify skill is characterized by:

- **Voice**: Third-person dominant (**First-person**: 38.6%, **Second-person**: 0.0%, **Third-person**: 61.4%)
- **CoT availability**: Always present (100.0%)
- **Self-correction**: 100.0% of traces contain corrections
- **Hypothesis-driven**: 27.2% of traces use hypothesis testing
- **Same-turn fix**: 24.3% involve mid-turn course correction
- **Connectors**: 1.89 per turn — top: because, since, thus, therefore

### Opener Words

| Opener | Frequency |
|--------|-----------|
| Alright | 66.0% |
| Okay | 14.6% |
| All | 11.7% |
| The | 6.8% |
| I | 1.0% |

### Step Transition Matrix (Top Transitions)

| From → To | Probability |
|-----------|-------------|
| ACKNOWLEDGE → VERIFY | 15.4% |
| ACKNOWLEDGE → PLAN | 15.4% |
| VERIFY → PLAN | 14.1% |
| PLAN → VERIFY | 13.2% |
| VERIFY → ACKNOWLEDGE | 5.1% |
| PLAN → EXECUTE | 4.7% |
| PLAN → ACKNOWLEDGE | 4.3% |
| ACKNOWLEDGE → SCOPE | 3.9% |
| ACKNOWLEDGE → EXECUTE | 3.9% |
| SCOPE → PLAN | 3.0% |
| VERIFY → EXECUTE | 2.6% |
| EXECUTE → VERIFY | 2.6% |

## The Natural Verify Flow

Do NOT write formal section headers. Follow this natural reasoning flow:

### 1. ACKNOWLEDGE — Context Awareness

Start with 'Alright' or 'Alright'

- Opener 'Alright' is most frequent
- Step coverage: 103.9%
- NEVER write 'ACKNOWLEDGE:' as a header

### 2. PLAN — Approach Design

Plan your approach step by step. PLAN transitions most frequently to VERIFY and EXECUTE.

- Step coverage: 94.2%
- Use connectors: because, since, thus
- Consider trade-offs inline

### 3. EXECUTE — Take Action

State what you'll do, then do it.

- Step coverage: 27.2%
- EXECUTE transitions most to PLAN (iterative development)

### 4. VERIFY — Validate

After actions, verify correctness.

- Step coverage: 79.6%
- 24.3% of turns involve same-turn verification

### 5. ITERATE — Self-Correct

Self-correction is universal (100.0%) — this is normal, not a failure.

- Avg 7.50 corrections per trace
- 27.2% of traces are hypothesis-driven
- Use 'Actually' or 'However' for corrections

## Behavioral Patterns

### Pattern: Highest Self-Correction Rate (7.5/trace)

Verify mode has the highest average self-corrections of any skill. Verification naturally involves checking and re-checking.

**Evidence**: 7.5 avg self-corrections per trace — 27% higher than code mode.

### Pattern: ACKNOWLEDGE→VERIFY Direct Entry

Verify mode often goes ACKNOWLEDGE→VERIFY directly, skipping PLAN. Verification can be immediate.

**Evidence**: ACKNOWLEDGE→VERIFY (0.15), ACKNOWLEDGE→PLAN (0.15) — tied.

### Pattern: PLAN→VERIFY→PLAN Loop

Verify mode cycles: PLAN what to test → VERIFY results → RE-PLAN based on findings. This is unique to verify mode.

**Evidence**: VERIFY→PLAN (0.14), PLAN→VERIFY (0.13) — bidirectional loop.

### Pattern: Highest Same-Turn Fix Rate (24.3%)

1 in 4 verify traces involves mid-turn correction. Verification frequently catches issues requiring immediate fix.

**Evidence**: 24.3% same-turn fix rate — highest of all skills.

### Pattern: 'Alright' Opener (66%)

Verify mode opens with 'Alright' 66% of the time — self-narrative framing before verification.

**Evidence**: 66.0% 'Alright' opener, 14.6% 'Okay', 11.7% 'All'.

### Pattern: VERIFY→PLAN as Primary Feedback

The most common transition from VERIFY is back to PLAN — verification findings trigger re-planning.

**Evidence**: VERIFY→PLAN at 0.14 — higher than VERIFY→ACKNOWLEDGE (0.05).

### Pattern: Thorough Step Coverage

Verify mode has the most comprehensive step coverage: ACK (1.04), PLAN (0.94), EXECUTE (0.27), VERIFY (0.80), GATHER (0.07).

**Evidence**: Highest VERIFY coverage (0.80), widest step distribution of any skill.

### Pattern: First-Person Verification Narrative

Verify mode narrates in first-person ('I should test', 'let me verify', 'I need to check').

**Evidence**: 38.6% first-person, 61.4% third-person pronouns.

### Pattern: Common Openers

Frequent utterance starters: Alright, Okay, All, The, I

**Frequency**: 100.0%

### Pattern: Self Correction

Frequently corrects reasoning mid-turn

**Frequency**: 100.0%

### Pattern: Acknowledge Then Execute

Always acknowledges context before acting

**Frequency**: 103.9%

### Pattern: Reasoning Chaining

Uses connectors like because, since, thus

**Frequency**: 37.9%

## Key Statistics from 500 Traces (Verify Subset)

### CoT Structure
- **Avg tokens**: 417.7 (median: 390.0)
- **Avg paragraphs**: 7.5
- **Avg sentences**: 16.0
- **Avg characters**: 2632.0
- **Max tokens**: 947, **Min tokens**: 199

### Reasoning Style
- **Pronoun distribution**: **First-person**: 38.6%, **Second-person**: 0.0%, **Third-person**: 61.4%
- **Connectors per turn**: 1.89
- **Top connectors**: because, since, thus, therefore, given that
- **Self-corrections per trace**: 7.50

### Behavior
- **Hypothesis-driven**: 27.2%
- **Multi-investigation rate**: 0.0%
- **Same-turn fix rate**: 24.3%
- **Step coverage**: ACK 103.9%, SCOPE 14.6%, GATHER 6.8%, PLAN 94.2%, EXECUTE 27.2%, VERIFY 79.6%

## Anti-Patterns

- ❌ **Acting Without Scope** (85.4%) — Proceeding without confirming requirements
- ❌ Formal section headers (## ACKNOWLEDGE, ## SCOPE, etc.) — Fable 5 never uses them
- ❌ Using 'Oops' for self-correction — use 'Actually' or 'However' instead
- ❌ Making changes without understanding context first
- ❌ Skipping verification after changes
- ❌ Planning once without iterative refinement
- ❌ Expressing certainty when hedging is appropriate
- ❌ Writing one-sentence reasoning before deciding
