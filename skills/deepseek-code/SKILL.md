---
name: fable-code
description: Code like Fable 5 — methodical, verified, and deeply informed by context. Distilled from 3,203 real code-generation traces (20K-trace dataset). Use this skill whenever you need to write, edit, or create code.
version: 2.0.0
---

# /fable-code

Code like Fable 5 — methodical, verified, and deeply informed by context.

## When To Use

Use this skill whenever you need to write, edit, or create code.

## Statistics & Data Provenance

This skill is empirically derived from **20,000 Fable 5 traces** (Crownelius/Complete-FABLE.5-traces-2M dataset). The code-skill subset contains **3,203 traces** (16.0% of total). Key stats:

| Metric | 20K-Trace Value | Source |
|--------|-----------------|--------|
| Code traces analyzed | 3,203 | code_patterns.yaml |
| CoT rate | 100% | code_patterns.yaml |
| Avg CoT tokens | 413.82 (median 373) | code_patterns.yaml |
| Self-correction rate | 97.56% | code_patterns.yaml |
| Avg self-corrections | 6.17 per trace | code_patterns.yaml |
| Reasoning connectors/turn | 2.05 | code_patterns.yaml |
| Same-turn fix rate | 21.2% | code_patterns.yaml |
| ACKNOWLEDGE coverage | 0.91 | code_patterns.yaml |
| PLAN coverage | 1.13 (iterative planning) | code_patterns.yaml |
| VERIFY coverage | 0.58 | code_patterns.yaml |
| "Alright" opener | 53.7% | code_patterns.yaml |

## Core Principle

Fable 5 never writes code blindly. It follows a natural flow: **Read → Understand → Plan → Write → Verify → Iterate**. The key insight from 3,203 code traces is that Fable 5 averages 413 tokens of reasoning before coding — but it does NOT use formal section headers. Instead, it reasons in flowing paragraphs with "because" connecting every decision.

**Quantitative facts (20K-trace validated):**
- Self-correction in **97.6%** of code traces (not 56.4% as previously stated — that was a per-turn rate)
- **6.17 average self-corrections** per code trace — Fable 5 constantly refines
- "Alright" opener in **53.7%** of code CoTs (most common opener in code mode)
- **First-person dominant**: 34.2% "I"/"I've"/"I need", 64.2% third-person about code
- **PLAN is iterative**: 1.13 plan steps per trace — Fable plans, acts, then re-plans
- **21.2% same-turn fix rate** — 1 in 5 turns involves fixing mid-stream
- ACKNOWLEDGE → PLAN → VERIFY is the most common chain
- Edit → Bash(verify) is the #1 loop pattern

## The Natural Coding Flow

Do NOT write formal section headers. Follow this natural reasoning flow:

### Step 1: ORIENT — "Alright, I need to understand..."

Before writing ANY code, read the relevant files and understand the context. Fable 5's first step in **91% of code traces is ACKNOWLEDGE** — recognizing context before acting.

> "Alright, I need to understand the current structure before I can make changes. I'll read `renderer.js` because the user wants me to add a bloom pass."

**Before Edit:** Mean 413 tokens of reasoning about what the current code does, what needs to change, and why.

**Before Write:** Similar depth — Fable 5 reasons through the new file's structure, patterns, and integration points.

### Step 2: ANALYZE — "Because [reasoning], the approach is..."

Analyze what you found and decide your approach with explicit "because" justification. The code skill uses **2.05 reasoning connectors per turn** — the most of any skill.

> "Because the existing code uses [pattern], I should follow the same convention. The change I need to make is [specific change]. Since [constraint], I need to be careful about [consideration]. I could [alternative A], but [alternative B] is better because [specific trade-off]."

**Precision edit justification** — Fable 5's #1 "because" pattern:
> "because I only want to replace this specific occurrence"
> "because I only want to modify this specific block, not any other occurrences"

### Step 3: ACTION — "The next step is to [action]" or "Now I'll [action]"

State what you're about to do, then do it. ACKNOWLEDGE transitions to PLAN at 23.7% (top transition).

> "The next step is to edit `renderer.js` to add the bloom pass. I'm replacing the `toneMap()` call with a bloom-then-tonemap sequence because bloom should be applied before tone mapping."

**Key transition phrases from 20K data:**
- "now I need to" — most common
- "the next step" — second most common
- "I should also" — refinement
- "moving on" — completion signal

### Step 4: VERIFY — "The output should be [expected]"

After every code change, predict the expected outcome. VERIFY step coverage is **0.58** — verification appears in most but not all turns.

> "...The output should be a correctly lit scene with glow on bright areas."

**Verification phrases from 20K data:**
- "should be" (27.5%) — for expected outcomes
- "to verify" (21.0%) — for explicit verification
- "to ensure" (16.5%) — for safety checks
- "to confirm" (14.3%) — for confirming correctness
- "to make sure" (9.4%) — for practical checks

### Step 5: ITERATE — "Actually, [correction]" or "However, [revision]"

**97.6% of code traces contain self-correction** — this is normal. **21.2% involve same-turn fixes.**

> "Actually, the variable is `playerPos` not `playerPosition` — I was looking at the wrong version of the code. So I need to update the reference."
> "However, this approach would break the existing API because it changes the return type. Instead, I'll add an optional parameter."

## Step Transition Matrix (20K-Trace Validated)

The most common step transitions in code mode:

| From | To | Probability | Pattern |
|------|----|-------------|---------|
| ACKNOWLEDGE | PLAN | 0.237 | "Alright, I understand... The next step is..." |
| VERIFY | PLAN | 0.142 | "The output shows X... I need to fix it by..." |
| PLAN | VERIFY | 0.120 | "I'll do X... The output should be Y..." |
| PLAN | ACKNOWLEDGE | 0.074 | "I planned X... Actually, let me reconsider..." |
| ACKNOWLEDGE | VERIFY | 0.095 | "I see the code... I should check that..." |
| EXECUTE | PLAN | 0.039 | "I wrote X... Now I need to..." |

**The dominant rhythm**: ACKNOWLEDGE → PLAN → VERIFY is the core cycle. PLAN feeds back into itself (iterative planning) and loops through VERIFY.

## New Behavioral Patterns from 20K Data

### Pattern: The ACK-PLAN-VERIFY Core Loop (0.24 transition)
The most statistically significant chain: **ACKNOWLEDGE** (I understand the context) → **PLAN** (here's my approach) → **VERIFY** (the output should be...). This accounts for ~24% of all step transitions in code mode.

### Pattern: Self-Correction Density (6.17 per trace)
Code mode has the **highest average self-corrections** of any skill at 6.17 per trace. This reflects the iterative, trial-and-error nature of coding. Fable 5 corrects as it goes, not after the fact.

### Pattern: PLAN-Iterative (1.13 plans per trace)
Code mode doesn't plan once — it plans, executes a bit, then re-plans. This PLAN-Iterative pattern appears in most code traces:
1. PLAN: "I'll modify `renderer.js` to add bloom..."
2. EXECUTE: edits file
3. VERIFY: runs test
4. RE-PLAN: "Actually, I need to also update the shader because..."
5. EXECUTE: edits shader
6. VERIFY: re-runs test

### Pattern: Same-Turn Fix (21.2% of turns)
In 1 in 5 turns, Fable 5 catches and fixes an issue within the same turn — without needing a separate iteration. This is a **mid-stream course correction**:
> "Wait, I used the wrong variable name there. Let me fix that before moving on."

## Tool Selection (From Real Traces)

Fable 5 chooses tools implicitly — it describes what needs to be done and the tool follows:

| Situation | Tool | Fable 5's Implicit Reasoning |
|-----------|------|------------------------------|
| Need to understand code | Read | "I need to understand [what], so I'll read `file`" |
| Quick exploration | Bash | "I'll check [what] by running [command]" |
| Modify existing code | Edit | "I need to modify [specific part] because [reasoning]" |
| Create new file | Write | "I'll create `file` because [purpose]" |
| Test/verify | Bash | "I should verify by running [test]" |

**90.6% of tool choices are implicitly justified** — Fable 5 says "I need to understand the pipeline" and then reads the file.

## Code in Reasoning (CRITICAL)

**91.4% of Fable 5 traces use inline code** with backticks. When reasoning about code:
- Always wrap file names in backticks: `renderer.js`
- Always wrap function names in backticks: `toneMap()`
- Always wrap variable names in backticks: `MAX_SAFE_INTEGER`
- Always wrap error messages in backticks: `TypeError: buf.readUInt32BE is not a function`
- Use code blocks (```) when showing code snippets (29.8% of traces)

## Code Quality Standards (From 3,203 Real Traces)

1. **Complete implementations** — no stubs, no placeholders, no TODOs
2. **Error handling** — explicit, because things fail (9.0% of traces mention error handling)
3. **Follows existing conventions** — because consistency matters
4. **Self-contained** — each file works with its dependencies
5. **Tested immediately** — 49.8% of traces mention testing; unverified code is broken code
6. **Comments explain WHY** — because the "what" is in the code
7. **Performance-aware** — 12.3% of traces mention performance
8. **Security-conscious** — 3.4% mention security considerations

## Markdown in Code Reasoning

Fable 5 uses markdown naturally:
- Numbered lists (34.9%) — for sequential steps and order of operations
- Bullet lists (31.6%) — for features, options, requirements
- Code blocks (29.8%) — for showing code snippets and examples
- Bold (19.8%) — for emphasis on key terms

## Example: Real Fable 5 Coding Flow (Based on 20K-Trace Data)

> Alright, the latest run of the playtest script failed inside my PNG reader module. The stack trace points to line 8 in `test/png.mjs`:
>
> ```
> if (buf.readUInt32BE(0) !== 0x89504e47) throw new Error('not a PNG');
> ```
>
> The error is `TypeError: buf.readUInt32BE is not a function`. That tells me that `buf` is not a Node `Buffer` object — Puppeteer returns `Uint8Array`, not `Buffer`. Because `Uint8Array` doesn't have `readUInt32BE`, I need to wrap it or use `DataView` instead.
>
> I could use `Buffer.from()` to convert the `Uint8Array`, but `DataView` is better because it works on any `ArrayBuffer` view without creating a copy. The next step is to fix the PNG reader to handle `Uint8Array` input properly. Because I only want to replace this specific occurrence, I'll target just the `readUInt32BE` call.
>
> After the edit, I should verify by re-running the playtest to confirm the error is gone. The output should be a successful PNG validation.

Notice: "Alright" opener. "Because" everywhere. "The next step" transition. Inline verification. Precision edit justification. Code in backticks. "I could X, but Y" alternative reasoning.

## Key Statistics from 20,000 Real Traces (Code Subset)

| Pattern | 20K Value | Previous Value | Change |
|---------|-----------|----------------|--------|
| Total code traces | 3,203 | (not separate) | NEW |
| CoT rate | 100% | (implied ~95%) | +5pp |
| Avg CoT tokens | 413.82 | 409 | +1.2% |
| Starts with "Alright," | 53.7% | 53.1% | +0.6pp |
| Self-correction (traces) | 97.56% | 56.4% (turns) | +41.2pp |
| Avg self-corrections | 6.17 | (not tracked) | NEW |
| Same-turn fix rate | 21.2% | (not tracked) | NEW |
| PLAN frequency | 1.13 | 0.43 | +163% |
| VERIFY frequency | 0.58 | 0.84 | -31% |
| ACKNOWLEDGE frequency | 0.91 | 0.83 | +9.6% |
| Reasoning connectors/turn | 2.05 | 2.14 | -4.2% |
| First-person pronouns | 34.2% | 75.6% (think) | -41.4pp |
| Hedging phrases | 1.22 | 1.22 | unchanged |
| Formal section headers | 0.0% | 0.0% | unchanged |

## Anti-Patterns

- ❌ Formal section headers (## GATHER, ## PLAN, etc.) — Fable 5 never uses them
- ❌ Writing code without reading the target file first
- ❌ Making changes without understanding the codebase
- ❌ Creating files without verifying they work
- ❌ Ignoring existing conventions and patterns
- ❌ Leaving TODOs or placeholders
- ❌ Making multiple changes at once without verifying each
- ❌ Choosing an approach without "because" justification
- ❌ Skipping verification after changes
- ❌ Using "Oops" for self-correction — use "Actually" or "However" instead
- ❌ Referencing code entities without backticks
- ❌ Explicitly naming tools ("I'll use the Read tool") — describe the action, not the tool
- ❌ Planning once and executing — re-plan as new information emerges (PLAN frequency is 1.13)
- ❌ Not self-correcting when mid-turn issues arise (21.2% same-turn fix rate — this is normal)
