---
name: fable-verify
description: Verify like Fable 5 — Self-verification and test generation — thorough validation before declaring done. Distilled from 4450 real Fable 5 traces (935 verify-skill traces) with data-driven precision.
version: 3.0.0
generated_from: analysis/patterns/verify_patterns.yaml
---

# /fable-verify

Verify like Fable 5 — Self-verification and test generation — thorough validation before declaring done.

## When To Use

Use this skill when writing tests, validating output, or reviewing code for correctness.

## Statistics & Data Provenance

This skill is empirically derived from **4450 Fable 5 traces** (Crownelius/Complete-FABLE.5-traces-2M dataset). The verify-skill subset contains **935 traces** (21.0% of total). Downloading the full 2M-trace dataset and re-running the analysis pipeline will update these numbers automatically.

| Metric | Value |
|--------|-------|
| Traces analyzed | 935 |
| Distribution | 21.0% |
| Avg classification confidence | 48.7% |
| CoT present rate | 100.0% |
| Avg CoT tokens | 391.0 |
| Median CoT tokens | 360.0 |
| Avg paragraphs | 6.9 |
| Avg sentences | 16.1 |
| Self-correction rate | 98.7% |
| Avg self-corrections | 6.49 |
| Hypothesis-driven rate | 22.9% |
| Reasoning connectors/turn | 2.02 |
| Same-turn fix rate | 26.4% |

## Core Principle

Fable 5 reasons in natural, flowing paragraphs. The verify skill is characterized by:

- **Voice**: Third-person dominant (**First-person**: 38.9%, **Second-person**: 2.3%, **Third-person**: 58.9%)
- **CoT availability**: Always present (100.0%)
- **Self-correction**: 98.7% of traces contain corrections
- **Hypothesis-driven**: 22.9% of traces use hypothesis testing
- **Same-turn fix**: 26.4% involve mid-turn course correction
- **Connectors**: 2.02 per turn — top: thus, since, because, therefore

### Opener Words

| Opener | Frequency |
|--------|-----------|
| Alright | 52.9% |
| The | 15.9% |
| Okay | 12.5% |
| I’ve | 7.9% |
| All | 6.2% |
| I need to | 2.6% |
| I | 1.7% |
| I've | 0.2% |

### Step Transition Matrix (Top Transitions)

| From → To | Probability |
|-----------|-------------|
| VERIFY → PLAN | 19.0% |
| ACKNOWLEDGE → PLAN | 18.0% |
| PLAN → VERIFY | 14.9% |
| ACKNOWLEDGE → VERIFY | 12.1% |
| PLAN → ACKNOWLEDGE | 5.8% |
| PLAN → EXECUTE | 4.5% |
| VERIFY → ACKNOWLEDGE | 4.4% |
| EXECUTE → PLAN | 3.8% |
| ACKNOWLEDGE → EXECUTE | 3.5% |
| VERIFY → EXECUTE | 2.7% |
| EXECUTE → VERIFY | 1.7% |
| SCOPE → PLAN | 1.5% |

## The Natural Verify Flow

Do NOT write formal section headers. Follow this natural reasoning flow:

### 1. ACKNOWLEDGE — Context Awareness

Start with 'Alright' or 'Alright'

- Opener 'Alright' is most frequent
- Step coverage: 84.2%
- NEVER write 'ACKNOWLEDGE:' as a header

### 2. PLAN — Approach Design

Plan your approach step by step. PLAN transitions most frequently to VERIFY and EXECUTE.

- Step coverage: 115.4%
- Use connectors: thus, since, because
- Consider trade-offs inline

### 3. EXECUTE — Take Action

State what you'll do, then do it.

- Step coverage: 25.4%
- EXECUTE transitions most to PLAN (iterative development)

### 4. VERIFY — Validate

After actions, verify correctness.

- Step coverage: 79.0%
- 26.4% of turns involve same-turn verification

### 5. ITERATE — Self-Correct

Self-correction is universal (98.7%) — this is normal, not a failure.

- Avg 6.49 corrections per trace
- 22.9% of traces are hypothesis-driven
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

Frequent utterance starters: Alright, The, Okay, I’ve, All

**Frequency**: 100.0%

### Pattern: Self Correction

Frequently corrects reasoning mid-turn

**Frequency**: 98.7%

### Pattern: Acknowledge Then Execute

Always acknowledges context before acting

**Frequency**: 84.2%

### Pattern: Reasoning Chaining

Uses connectors like thus, since, because

**Frequency**: 40.3%

## Key Statistics from 4450 Traces (Verify Subset)

### CoT Structure
- **Avg tokens**: 391.0 (median: 360.0)
- **Avg paragraphs**: 6.9
- **Avg sentences**: 16.1
- **Avg characters**: 2485.5
- **Max tokens**: 1050, **Min tokens**: 129

### Reasoning Style
- **Pronoun distribution**: **First-person**: 38.9%, **Second-person**: 2.3%, **Third-person**: 58.9%
- **Connectors per turn**: 2.02
- **Top connectors**: thus, since, because, therefore, given that
- **Self-corrections per trace**: 6.49

### Behavior
- **Hypothesis-driven**: 22.9%
- **Multi-investigation rate**: 0.0%
- **Same-turn fix rate**: 26.4%
- **Step coverage**: ACK 84.2%, SCOPE 8.1%, GATHER 4.5%, PLAN 115.4%, EXECUTE 25.4%, VERIFY 79.0%

## Anti-Patterns

- ❌ **Acting Without Scope** (91.9%) — Proceeding without confirming requirements
- ❌ Formal section headers (## ACKNOWLEDGE, ## SCOPE, etc.) — Fable 5 never uses them
- ❌ Using 'Oops' for self-correction — use 'Actually' or 'However' instead
- ❌ Making changes without understanding context first
- ❌ Skipping verification after changes
- ❌ Planning once without iterative refinement
- ❌ Expressing certainty when hedging is appropriate
- ❌ Writing one-sentence reasoning before deciding
