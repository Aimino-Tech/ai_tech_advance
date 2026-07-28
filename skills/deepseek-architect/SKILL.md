---
name: fable-architect
description: Architect like Fable 5 — System decomposition and design — planning interfaces before implementation. Distilled from 500 real Fable 5 traces (3 architect-skill traces) with data-driven precision.
version: 3.0.0
generated_from: analysis/patterns/architect_patterns.yaml
---

# /fable-architect

Architect like Fable 5 — System decomposition and design — planning interfaces before implementation.

## When To Use

Use this skill when designing systems, choosing architectures, or planning component structure.

## Statistics & Data Provenance

This skill is empirically derived from **500 Fable 5 traces** (Crownelius/Complete-FABLE.5-traces-2M dataset). The architect-skill subset contains **3 traces** (0.6% of total). Downloading the full 2M-trace dataset and re-running the analysis pipeline will update these numbers automatically.

| Metric | Value |
|--------|-------|
| Traces analyzed | 3 |
| Distribution | 0.6% |
| Avg classification confidence | 45.1% |
| CoT present rate | 100.0% |
| Avg CoT tokens | 299.7 |
| Median CoT tokens | 239.0 |
| Avg paragraphs | 4.3 |
| Avg sentences | 13.0 |
| Self-correction rate | 66.7% |
| Avg self-corrections | 3.33 |
| Hypothesis-driven rate | 66.7% |
| Reasoning connectors/turn | 1.33 |
| Same-turn fix rate | 0.0% |

## Core Principle

Fable 5 reasons in natural, flowing paragraphs. The architect skill is characterized by:

- **Voice**: Third-person dominant (**First-person**: 41.2%, **Second-person**: 0.0%, **Third-person**: 58.8%)
- **CoT availability**: Always present (100.0%)
- **Self-correction**: 66.7% of traces contain corrections
- **Hypothesis-driven**: 66.7% of traces use hypothesis testing
- **Same-turn fix**: 0.0% involve mid-turn course correction
- **Connectors**: 1.33 per turn — top: therefore, since, thus

### Opener Words

| Opener | Frequency |
|--------|-----------|
| The | 66.7% |
| Alright | 33.3% |

### Step Transition Matrix (Top Transitions)

| From → To | Probability |
|-----------|-------------|
| ACKNOWLEDGE → PLAN | 33.3% |
| PLAN → VERIFY | 33.3% |
| VERIFY → PLAN | 33.3% |

## The Natural Architect Flow

Do NOT write formal section headers. Follow this natural reasoning flow:

### 1. ACKNOWLEDGE — Context Awareness

Start with 'The' or 'Alright'

- Opener 'The' is most frequent
- Step coverage: 33.3%
- NEVER write 'ACKNOWLEDGE:' as a header

### 2. PLAN — Approach Design

Plan your approach step by step. PLAN transitions most frequently to VERIFY and EXECUTE.

- Step coverage: 100.0%
- Use connectors: therefore, since, thus
- Consider trade-offs inline

### 3. EXECUTE — Take Action

State what you'll do, then do it.

- Step coverage: 0.0%
- EXECUTE transitions most to PLAN (iterative development)

### 4. VERIFY — Validate

After actions, verify correctness.

- Step coverage: 66.7%
- 0.0% of turns involve same-turn verification

### 5. ITERATE — Self-Correct

Self-correction is common (66.7%) — this is normal, not a failure.

- Avg 3.33 corrections per trace
- 66.7% of traces are hypothesis-driven
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

Frequent utterance starters: The, Alright

**Frequency**: 100.0%

### Pattern: Self Correction

Frequently corrects reasoning mid-turn

**Frequency**: 66.7%

### Pattern: Hypothesis Driven Debugging

Forms and tests hypotheses before fixing

**Frequency**: 66.7%

### Pattern: Acknowledge Then Execute

Always acknowledges context before acting

**Frequency**: 33.3%

### Pattern: Reasoning Chaining

Uses connectors like therefore, since, thus

**Frequency**: 26.7%

## Key Statistics from 500 Traces (Architect Subset)

### CoT Structure
- **Avg tokens**: 299.7 (median: 239.0)
- **Avg paragraphs**: 4.3
- **Avg sentences**: 13.0
- **Avg characters**: 1884.3
- **Max tokens**: 532, **Min tokens**: 128

### Reasoning Style
- **Pronoun distribution**: **First-person**: 41.2%, **Second-person**: 0.0%, **Third-person**: 58.8%
- **Connectors per turn**: 1.33
- **Top connectors**: therefore, since, thus
- **Self-corrections per trace**: 3.33

### Behavior
- **Hypothesis-driven**: 66.7%
- **Multi-investigation rate**: 0.0%
- **Same-turn fix rate**: 0.0%
- **Step coverage**: ACK 33.3%, SCOPE 0.0%, GATHER 0.0%, PLAN 100.0%, EXECUTE 0.0%, VERIFY 66.7%

## Anti-Patterns

- ❌ Formal section headers (## ACKNOWLEDGE, ## SCOPE, etc.) — Fable 5 never uses them
- ❌ Using 'Oops' for self-correction — use 'Actually' or 'However' instead
- ❌ Making changes without understanding context first
- ❌ Skipping verification after changes
- ❌ Planning once without iterative refinement
- ❌ Expressing certainty when hedging is appropriate
- ❌ Writing one-sentence reasoning before deciding
