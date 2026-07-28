---
name: fable-think
description: Think like Fable 5 — Natural, flowing, purposeful reasoning distilled from chain-of-thought traces. Distilled from 500 real Fable 5 traces (6 think-skill traces) with data-driven precision.
version: 3.0.0
generated_from: analysis/patterns/think_patterns.yaml
---

# /fable-think

Think like Fable 5 — Natural, flowing, purposeful reasoning distilled from chain-of-thought traces.

## When To Use

Use this skill EVERY TIME before writing code, making decisions, or taking action. This is the foundational reasoning skill that all other skills build upon.

## Statistics & Data Provenance

This skill is empirically derived from **500 Fable 5 traces** (Crownelius/Complete-FABLE.5-traces-2M dataset). The think-skill subset contains **6 traces** (1.2% of total). Downloading the full 2M-trace dataset and re-running the analysis pipeline will update these numbers automatically.

| Metric | Value |
|--------|-------|
| Traces analyzed | 6 |
| Distribution | 1.2% |
| Avg classification confidence | 24.5% |
| CoT present rate | 66.7% |
| Avg CoT tokens | 393.2 |
| Median CoT tokens | 291.5 |
| Avg paragraphs | 6.5 |
| Avg sentences | 16.0 |
| Self-correction rate | 100.0% |
| Avg self-corrections | 2.50 |
| Hypothesis-driven rate | 25.0% |
| Reasoning connectors/turn | 1.75 |
| Same-turn fix rate | 25.0% |

## Core Principle

Fable 5 reasons in natural, flowing paragraphs. The think skill is characterized by:

- **Voice**: Third-person dominant (**First-person**: 50.0%, **Second-person**: 0.0%, **Third-person**: 50.0%)
- **CoT availability**: Not always present (66.7%)
- **Self-correction**: 100.0% of traces contain corrections
- **Hypothesis-driven**: 25.0% of traces use hypothesis testing
- **Same-turn fix**: 25.0% involve mid-turn course correction
- **Connectors**: 1.75 per turn — top: therefore, since, given that, because

### Opener Words

| Opener | Frequency |
|--------|-----------|
| The | 75.0% |
| Alright | 25.0% |

### Step Transition Matrix (Top Transitions)

| From → To | Probability |
|-----------|-------------|
| PLAN → VERIFY | 12.5% |
| PLAN → ACKNOWLEDGE | 12.5% |
| VERIFY → PLAN | 12.5% |
| VERIFY → ACKNOWLEDGE | 12.5% |
| ACKNOWLEDGE → PLAN | 12.5% |
| ACKNOWLEDGE → VERIFY | 12.5% |
| ACKNOWLEDGE → SCOPE | 12.5% |
| SCOPE → EXECUTE | 12.5% |

## The Natural Think Flow

Do NOT write formal section headers. Follow this natural reasoning flow:

### 1. ACKNOWLEDGE — Context Awareness

Start with 'The' or 'Alright'

- Opener 'The' is most frequent
- Step coverage: 75.0%
- NEVER write 'ACKNOWLEDGE:' as a header

### 2. PLAN — Approach Design

Plan your approach step by step. PLAN transitions most frequently to VERIFY and EXECUTE.

- Step coverage: 125.0%
- Use connectors: therefore, since, given that
- Consider trade-offs inline

### 3. EXECUTE — Take Action

State what you'll do, then do it.

- Step coverage: 25.0%
- EXECUTE transitions most to PLAN (iterative development)

### 4. VERIFY — Validate

After actions, verify correctness.

- Step coverage: 50.0%
- 25.0% of turns involve same-turn verification

### 5. ITERATE — Self-Correct

Self-correction is universal (100.0%) — this is normal, not a failure.

- Avg 2.50 corrections per trace
- 25.0% of traces are hypothesis-driven
- Use 'Actually' or 'However' for corrections

## Behavioral Patterns

### Pattern: The-Then Conditional Reasoning

Think mode explores conditional scenarios: 'If [condition], then [outcome]'. This is the top reasoning connector pattern. 'If' and 'But' are the #1 and #2 connectors in think mode — higher than any other skill.

**Evidence**: 'If' and 'But' are the top reasoning connectors; think mode explores trade-offs and scenarios.

### Pattern: PLAN-Iterative (1.08+ Plans Per Trace)

Think mode doesn't plan once — it re-plans as new information emerges. Each ACKNOWLEDGE often triggers a new PLAN cycle.

**Evidence**: PLAN frequency exceeds 1.0 per trace in all skills; tools re-evaluate after each context shift.

### Pattern: ACKNOWLEDGE→PLAN Core Loop

The most statistically significant chain: ACKNOWLEDGE (I understand) → PLAN (here's my approach). This accounts for the highest transition probability in all skills.

**Evidence**: ACKNOWLEDGE→PLAN transition is consistently the highest probability across all 5 skills.

### Pattern: Self-Correction Is Universal

Self-correction appears in ~98% of traces. This is normal behavior, not a failure mode. Use 'Actually' or 'However' as correction markers.

**Evidence**: 97-100% self-correction rate across all skills; 'actually' is the #1 correction marker.

### Pattern: VERIFY-Follows-PLAN Transition

After each PLAN, think mode verifies: 'The output should be...'. This is the second-highest transition in most skills.

**Evidence**: PLAN→VERIFY transition probability of 0.12-0.13 across skills.

### Pattern: The-Opener Dominance

Think mode starts with 'The' more than any other opener — subject-first thinking. This is unique to think mode.

**Evidence**: 'The' opener is 45-75% in think mode vs <17% in other skills.

### Pattern: Hypothesis-Driven Exploration

Think mode forms and evaluates hypotheses before reaching conclusions. Uses connectors like 'perhaps', 'could be', 'maybe'.

**Evidence**: 25-67% hypothesis-driven rate across skills; highest in architect and debug.

### Pattern: Third-Person Voice Preference

Think mode prefers third-person pronouns — analyzing systems and subjects rather than self-narrating.

**Evidence**: Third-person pronouns 50-66% across all skills; think mode is especially subject-focused.

### Pattern: Common Openers

Frequent utterance starters: The, Alright

**Frequency**: 66.7%

### Pattern: Self Correction

Frequently corrects reasoning mid-turn

**Frequency**: 100.0%

### Pattern: Acknowledge Then Execute

Always acknowledges context before acting

**Frequency**: 75.0%

### Pattern: Reasoning Chaining

Uses connectors like therefore, since, given that

**Frequency**: 35.0%

## Key Statistics from 500 Traces (Think Subset)

### CoT Structure
- **Avg tokens**: 393.2 (median: 291.5)
- **Avg paragraphs**: 6.5
- **Avg sentences**: 16.0
- **Avg characters**: 2430.2
- **Max tokens**: 773, **Min tokens**: 217

### Reasoning Style
- **Pronoun distribution**: **First-person**: 50.0%, **Second-person**: 0.0%, **Third-person**: 50.0%
- **Connectors per turn**: 1.75
- **Top connectors**: therefore, since, given that, because
- **Self-corrections per trace**: 2.50

### Behavior
- **Hypothesis-driven**: 25.0%
- **Multi-investigation rate**: 0.0%
- **Same-turn fix rate**: 25.0%
- **Step coverage**: ACK 75.0%, SCOPE 25.0%, GATHER 0.0%, PLAN 125.0%, EXECUTE 25.0%, VERIFY 50.0%

## Anti-Patterns

- ❌ Formal section headers (## ACKNOWLEDGE, ## SCOPE, etc.) — Fable 5 never uses them
- ❌ Using 'Oops' for self-correction — use 'Actually' or 'However' instead
- ❌ Making changes without understanding context first
- ❌ Skipping verification after changes
- ❌ Planning once without iterative refinement
- ❌ Expressing certainty when hedging is appropriate
- ❌ Writing one-sentence reasoning before deciding
