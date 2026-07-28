---
name: fable-architect
description: Architect like Fable 5 — System decomposition and design — planning interfaces before implementation. Distilled from 5000 real Fable 5 traces (80 architect-skill traces) with data-driven precision.
version: 3.0.0
generated_from: analysis/patterns/architect_patterns.yaml
---

# /fable-architect

Architect like Fable 5 — System decomposition and design — planning interfaces before implementation.

## When To Use

Use this skill when designing systems, choosing architectures, or planning component structure.

## Statistics & Data Provenance

This skill is empirically derived from **5000 Fable 5 traces** (Crownelius/Complete-FABLE.5-traces-2M dataset). The architect-skill subset contains **80 traces** (1.6% of total). Downloading the full 2M-trace dataset and re-running the analysis pipeline will update these numbers automatically.

| Metric | Value |
|--------|-------|
| Traces analyzed | 80 |
| Distribution | 1.6% |
| Avg classification confidence | 48.9% |
| CoT present rate | 100.0% |
| Avg CoT tokens | 368.3 |
| Median CoT tokens | 296.0 |
| Avg paragraphs | 5.5 |
| Avg sentences | 16.2 |
| Self-correction rate | 92.5% |
| Avg self-corrections | 5.96 |
| Hypothesis-driven rate | 42.5% |
| Reasoning connectors/turn | 1.75 |
| Same-turn fix rate | 5.0% |

## Core Principle

Fable 5 reasons in natural, flowing paragraphs. The architect skill is characterized by:

- **Voice**: Third-person dominant (**First-person**: 46.9%, **Second-person**: 2.5%, **Third-person**: 50.6%)
- **CoT availability**: Always present (100.0%)
- **Self-correction**: 92.5% of traces contain corrections
- **Hypothesis-driven**: 42.5% of traces use hypothesis testing
- **Same-turn fix**: 5.0% involve mid-turn course correction
- **Connectors**: 1.75 per turn — top: therefore, thus, since, because

### Opener Words

| Opener | Frequency |
|--------|-----------|
| The | 53.8% |
| Alright | 31.2% |
| I’ve | 7.5% |
| Okay | 3.8% |
| I need to | 2.5% |
| All | 1.2% |

### Step Transition Matrix (Top Transitions)

| From → To | Probability |
|-----------|-------------|
| ACKNOWLEDGE → PLAN | 40.8% |
| PLAN → ACKNOWLEDGE | 18.4% |
| PLAN → VERIFY | 8.2% |
| EXECUTE → PLAN | 7.1% |
| ACKNOWLEDGE → EXECUTE | 3.1% |
| ACKNOWLEDGE → SCOPE | 3.1% |
| PLAN → EXECUTE | 3.1% |
| VERIFY → PLAN | 3.1% |
| VERIFY → EXECUTE | 3.1% |
| SCOPE → PLAN | 3.1% |
| PLAN → SCOPE | 2.0% |
| ACKNOWLEDGE → VERIFY | 1.0% |

## The Natural Architect Flow

Do NOT write formal section headers. Follow this natural reasoning flow:

### 1. ACKNOWLEDGE — Context Awareness

Start with 'The' or 'Alright'

- Opener 'The' is most frequent
- Step coverage: 75.0%
- NEVER write 'ACKNOWLEDGE:' as a header

### 2. PLAN — Approach Design

Plan your approach step by step. PLAN transitions most frequently to VERIFY and EXECUTE.

- Step coverage: 111.2%
- Use connectors: therefore, thus, since
- Consider trade-offs inline

### 3. EXECUTE — Take Action

State what you'll do, then do it.

- Step coverage: 13.8%
- EXECUTE transitions most to PLAN (iterative development)

### 4. VERIFY — Validate

After actions, verify correctness.

- Step coverage: 12.5%
- 5.0% of turns involve same-turn verification

### 5. ITERATE — Self-Correct

Self-correction is universal (92.5%) — this is normal, not a failure.

- Avg 5.96 corrections per trace
- 42.5% of traces are hypothesis-driven
- Use 'Actually' or 'However' for corrections

## Behavioral Patterns

### Pattern: PLAN-Dominant Flow

Architect mode is dominated by planning. PLAN coverage is 1.0 — every architect trace includes explicit planning.

**Evidence**: PLAN 1.0 coverage; ACKNOWLEDGE 0.33; VERIFY 0.67.

### Pattern: Hypothesis-Driven Architecture

Architect mode evaluates design alternatives before committing. Hypothesis-driven rate is comparable to debug.

**Evidence**: 66.7% hypothesis-driven rate — trades off alternative approaches.

### Pattern: ACKNOWLEDGE→PLAN→VERIFY Chain

The classic chain: ACKNOWLEDGE context → PLAN the design → VERIFY the approach. This is the dominant sequence.

**Evidence**: ACKNOWLEDGE→PLAN (0.33), PLAN→VERIFY (0.33), VERIFY→PLAN (0.33).

### Pattern: Lower Self-Correction Rate

Architect mode self-corrects less than other skills (66.7%) — designs are more deliberate and pre-validated.

**Evidence**: 66.7% self-correction rate (lowest of all skills); 3.33 avg corrections.

### Pattern: 'The' and 'Alright' Openers

Architect mode is split between subject-first ('The' 66.7%) and self-narrative ('Alright' 33.3%) openings.

**Evidence**: 66.7% 'The' opener, 33.3% 'Alright'.

### Pattern: Third-Person System Thinking

Architect mode analyzes systems using third-person pronouns — the system, not the self, is the subject.

**Evidence**: 58.8% third-person, 41.2% first-person pronouns.

### Pattern: Connectors: Trade-off Evaluation

Architect mode uses 'therefore', 'since', and 'thus' for causal design reasoning.

**Evidence**: 1.33 connectors/turn; top: therefore, since, thus.

### Pattern: Common Openers

Frequent utterance starters: The, Alright, I’ve, Okay, I need to

**Frequency**: 100.0%

### Pattern: Self Correction

Frequently corrects reasoning mid-turn

**Frequency**: 92.5%

### Pattern: Hypothesis Driven Debugging

Forms and tests hypotheses before fixing

**Frequency**: 42.5%

### Pattern: Acknowledge Then Execute

Always acknowledges context before acting

**Frequency**: 75.0%

### Pattern: Reasoning Chaining

Uses connectors like therefore, thus, since

**Frequency**: 35.0%

## Key Statistics from 5000 Traces (Architect Subset)

### CoT Structure
- **Avg tokens**: 368.3 (median: 296.0)
- **Avg paragraphs**: 5.5
- **Avg sentences**: 16.2
- **Avg characters**: 2392.8
- **Max tokens**: 1351, **Min tokens**: 83

### Reasoning Style
- **Pronoun distribution**: **First-person**: 46.9%, **Second-person**: 2.5%, **Third-person**: 50.6%
- **Connectors per turn**: 1.75
- **Top connectors**: therefore, thus, since, because, hence
- **Self-corrections per trace**: 5.96

### Behavior
- **Hypothesis-driven**: 42.5%
- **Multi-investigation rate**: 0.0%
- **Same-turn fix rate**: 5.0%
- **Step coverage**: ACK 75.0%, SCOPE 6.2%, GATHER 1.2%, PLAN 111.2%, EXECUTE 13.8%, VERIFY 12.5%

## Anti-Patterns

- ❌ **Acting Without Scope** (93.8%) — Proceeding without confirming requirements
- ❌ **No Verification** (87.5%) — Completes work without verification step
- ❌ Formal section headers (## ACKNOWLEDGE, ## SCOPE, etc.) — Fable 5 never uses them
- ❌ Using 'Oops' for self-correction — use 'Actually' or 'However' instead
- ❌ Making changes without understanding context first
- ❌ Skipping verification after changes
- ❌ Planning once without iterative refinement
- ❌ Expressing certainty when hedging is appropriate
- ❌ Writing one-sentence reasoning before deciding
