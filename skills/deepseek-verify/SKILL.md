---
name: fable-verify
description: Verify like Fable 5 — obsessive, systematic, evidence-based quality assurance woven into your reasoning. Distilled from 935 real verification traces (20K-trace dataset). Use this skill when you have just written or modified code, need to confirm something works, are running tests, or need to validate output against requirements.
version: 2.0.0
---

# /fable-verify

Verify like Fable 5 — obsessive, systematic, evidence-based quality assurance woven into your reasoning.

## When To Use

Use this skill when you've just written or modified code, need to confirm something works, are running tests, or need to validate output against requirements.

## Statistics & Data Provenance

This skill is empirically derived from **20,000 Fable 5 traces** (Crownelius/Complete-FABLE.5-traces-2M dataset). The verify-skill subset contains **935 traces** (4.7% of total). Key stats:

| Metric | 20K-Trace Value | Source |
|--------|-----------------|--------|
| Verify traces analyzed | 935 | verify_patterns.yaml |
| CoT rate | 100% | verify_patterns.yaml |
| Avg CoT tokens | 391.01 (median 360) | verify_patterns.yaml |
| Self-correction rate | 98.72% | verify_patterns.yaml |
| Avg self-corrections | 6.49 per trace | verify_patterns.yaml |
| Reasoning connectors/turn | 2.02 | verify_patterns.yaml |
| Same-turn fix rate | 26.4% (highest) | verify_patterns.yaml |
| Hypothesis-driven rate | 22.9% | verify_patterns.yaml |
| ACKNOWLEDGE coverage | 0.84 | verify_patterns.yaml |
| PLAN coverage | 1.15 | verify_patterns.yaml |
| VERIFY coverage | 0.79 (highest) | verify_patterns.yaml |
| "Alright" opener | 52.9% | verify_patterns.yaml |
| Dataset confidence (avg) | 48.7% | combined_stats.json |

## Core Principle

Fable 5 verifies after **79% of its actions** (VERIFY step coverage: 0.79), but it does NOT use formal verification sections. Verification is **woven naturally** into the reasoning flow with a rich vocabulary of verification phrases. The most common verification tool is **Bash**, meaning Fable 5 verifies by running code, not by writing about verification.

**From 935 real verify traces:**
- **Self-correction: 98.72%** — near universal
- **Avg 6.49 self-corrections per trace** — second highest after debug
- **Same-turn fix rate: 26.4%** — highest of any skill; 1 in 4 turns involves a mid-turn fix
- **VERIFY step coverage: 0.79** — highest of any skill (second is code at 0.58)
- **"Alright" opener: 52.9%** — similar to code mode
- **PLAN coverage: 1.15** — even verify mode plans iteratively
- **Hypothesis-driven: 22.9%** — lowest; verify is more about checking than hypothesizing

**CRITICAL — Fable 5 uses all five verification phrases from the 20K data. You MUST use at least one of EACH:**
- `"should be"` (27.5% of CoTs) — for expected outcomes
- `"to verify"` (21.0% of CoTs) — for explicit verification intent
- `"to ensure"` (16.5% of CoTs) — for safety/quality checks
- `"to confirm"` (14.3% of CoTs) — for confirming correctness
- `"to make sure"` (9.4% of CoTs) — for practical everyday checks

## How Fable 5 Actually Verifies

### Verification Is Inline, Not A Section

Fable 5's full hierarchy of verification phrases (from 935 real verify traces):

| Phrase | % of Traces | Usage |
|--------|-------------|-------|
| "should be" | 27.5% | Expected outcomes |
| "to verify" | 21.0% | Explicit verification intent |
| "to ensure" | 16.5% | Safety/quality checks |
| "to confirm" | 14.3% | Confirming correctness |
| "to make sure" | 9.4% | Practical everyday checks |
| "I need to verify" | 8.5% | Action-oriented verification |
| "the expected" | 6.2% | Reference to expected results |
| "assert" | 5.6% | Test assertions |
| "validate" | 4.9% | Validation procedures |
| "I should verify" | 4.2% | Self-reminder to verify |
| "sanity check" | 3.3% | Quick reasonableness check |
| "smoke test" | 2.6% | Basic functionality test |

These are NOT section headers. They appear naturally in sentences:

> "I'll run the test script **to ensure** the fix doesn't break existing behavior."
> "The output **should be** a clean build with no errors."
> "Now I need **to confirm** this works **by** [method]."

### Verification Flow (From 20K-Trace Data)

The most common verify flow: **VERIFY → PLAN → ACKNOWLEDGE → EXECUTE → VERIFY**

Verification often reveals issues, which trigger re-planning. The same-turn fix rate of **26.4%** means 1 in 4 verification attempts results in an immediate fix within the same reasoning turn.

## The Natural Verification Flow

### After Writing Code:
> "Alright, I've created `game.js`. I should verify that the game loop runs correctly by running the playtest. The output should be a rendering of the 3D scene with player movement because the game loop handles input, physics, and rendering."

### After Editing Code:
> "Now I've edited the `toneMap()` function in `renderer.js`. I need to confirm this change works correctly and doesn't break the existing rendering because the tone mapper affects every pixel on screen. I'll run the playtest to ensure the scene still renders correctly."

### After Running Code:
> "The output shows 4 failed, 92 passed in 3.15s. Because there are still failures, I need to investigate. The test failures are likely in the new module because the existing tests all passed before my changes."

### After a Complex Feature:
> "I should do a sanity check on the full feature because the bloom pass touches every shader. I'll verify that basic rendering works, that bloom appears on bright areas, and that the FPS counter is still visible to ensure everything works end-to-end."

## Step Transition Matrix (20K-Trace Validated)

| From | To | Probability | Pattern |
|------|----|-------------|---------|
| VERIFY | PLAN | 0.190 | Verify fails → re-plan |
| ACKNOWLEDGE | PLAN | 0.180 | See context → plan verification |
| PLAN | VERIFY | 0.149 | Plan → execute verification |
| ACKNOWLEDGE | VERIFY | 0.121 | See context → directly verify |
| PLAN | ACKNOWLEDGE | 0.058 | Plan → reconsider context |
| VERIFY | ACKNOWLEDGE | 0.044 | Verify → acknowledge result |

**VERIFY→PLAN is the strongest transition (0.190)** — when verification fails, Fable 5 immediately re-plans. This is the highest VERIFY→PLAN rate of any skill.

**ACKNOWLEDGE→VERIFY is 0.121** — the highest direct ACK→VERIFY rate of any skill. In verify mode, Fable 5 acknowledges context then directly moves to verification.

## New Behavioral Patterns from 20K Data

### Pattern: Highest Same-Turn Fix Rate (26.4%)
Verify mode has the **highest same-turn fix rate** of any skill at 26.4%. This means verification catches issues that are fixed immediately within the same turn. This is the signature behavior of verify mode: observe → diagnose → fix → re-verify, all in one turn.

> "The output shows an error at line 42. Actually, I see the issue — I used `playerPos` instead of `playerPosition`. Let me fix that right away."

### Pattern: VERIFY→PLAN Loop (0.190)
The strongest transition in verify mode: verification reveals an issue, which triggers immediate re-planning. This is the "verify → find issue → fix → re-verify" loop.

### Pattern: ACKNOWLEDGE→VERIFY Direct (0.121)
Verify mode has the highest direct transition from ACKNOWLEDGE to VERIFY. Fable 5 in verify mode doesn't need to plan much — it sees the context and jumps straight to checking.

### Pattern: Lowest Hypothesis-Driven Rate (22.9%)
Verify mode is the least hypothesis-driven of all skills. Verification is about checking against known expectations, not forming new hypotheses. Use hedging (22.9% is low) — be direct about what you're checking.

## Verification Hierarchy (Applied Naturally)

### Level 1: Syntax Verification (Always)
After writing/editing: "The file should compile without syntax errors because [reasoning]."

### Level 2: Execution Verification (Usually)
After creating runnable code: "Now I'll run [command] to verify it executes without errors."

### Level 3: Behavioral Verification (Important Changes)
After implementing features: "I should verify that [specific behavior] works because [reasoning]."

### Level 4: Integration Verification (Major Changes)
After changes affecting multiple components: "I need to verify that [feature A] still works with [feature B]."

### Level 5: Regression Verification (Critical Changes)
After changes to core/shared code: "Because this change affects [shared component], I should run the full test suite to make sure nothing broke."

## Key Statistics from 20,000 Real Traces (Verify Subset)

| Pattern | 20K Value | Previous Value | Change |
|---------|-----------|----------------|--------|
| Total verify traces | 935 | (not separate) | NEW |
| CoT rate | 100% | (implied) | confirmed |
| Avg CoT tokens | 391.01 | ~409 | -4.4% |
| Starts with "Alright," | 52.9% | 53.1% | -0.2pp |
| Self-correction (traces) | 98.72% | 56.4% (turns) | +42.3pp |
| Avg self-corrections | 6.49 | (not tracked) | NEW |
| Same-turn fix rate | 26.4% | 37.4% (stated) | -11.0pp |
| VERIFY step coverage | 0.79 | 0.84 | -6.0% |
| PLAN frequency | 1.15 | 0.43 | +167% |
| Reasoning connectors/turn | 2.02 | 2.14 | -5.6% |
| "The" opener | 15.9% | (not tracked) | NEW |
| "Okay" opener | 12.5% | 10.8% | +1.7pp |

## "Should Be" — The #1 Verification Phrase

"Should be" appears in 27.5% of traces and is Fable 5's dominant verification expression. Use it for:
- Expected outcomes: "The output should be a clean build with no errors."
- Expected states: "After this change, the page should render the 3D scene correctly."
- Expected values: "The function should return `true` for valid inputs."
- Expected behavior: "The game should start the round when all players are ready."

## When Verification Fails

Fable 5 doesn't just note failures — it immediately diagnoses and fixes. **26.4% of turns contain a same-turn fix** — the highest rate of any skill.

When verification fails, use "Actually" or "However":

> "Actually, the test still fails because [root cause]. I need to [fix] because [reasoning]. After fixing, I should verify again to ensure [expected result]."
> "However, the output shows a different error — [new error]. This means [revised diagnosis] because [evidence]."

The failure response loop (natural, not formal):
1. Observe: "The output shows [failure]" or "Actually, [what went wrong]"
2. Diagnose: "Because [reasoning], the root cause is [cause]"
3. Fix: "The next step is to fix [action] because [reasoning]"
4. Re-verify: "The output should be [expected] to ensure the fix works correctly"

## Code Entity References in Verification

**91.4% of Fable 5 traces use inline code** with backticks. When verifying:
- Wrap expected values in backticks: "should return `0n`"
- Wrap error messages in backticks: "should not show `TypeError`"
- Wrap test names in backticks: "should pass `test_fibonacci`"
- Wrap file names in backticks: "should compile `renderer.js` without errors"

## Example: Real Fable 5 Verification Flow (Based on 20K-Trace Data)

> Alright, the recent edits should have addressed the rendering artifact. I added NaN checks and clamping because invalid color values could cause the black box. Now I need to confirm that these fixes actually eliminate the issue.
>
> Because the most straightforward way to verify is to re-run the playtest, I'll issue the Bash command. The output should show the black box gone in the screenshots because the NaN clamping prevents invalid values. If the artifact persists, I'll need to dig deeper because the issue might be in a different code path — perhaps the tone mapping stage rather than the ray-sphere intersection.

Notice: "Alright" opener. "Because" everywhere. "Should" for expected outcome. Inline verification. Fallback plan. "If X persists, I'll need to Y because Z." Code in backticks.

## Anti-Patterns

- ❌ Formal section headers (## VERIFY, ## CHECKLIST, etc.) — Fable 5 never uses them
- ❌ Assuming code works because it "looks right"
- ❌ Skipping verification for "simple" changes
- ❌ Only verifying the happy path
- ❌ Not checking for regressions after changes
- ❌ Seeing an error and immediately rewriting everything
- ❌ Not re-verifying after applying a fix
- ❌ Writing about verification without actually running code
- ❌ Using only "to ensure" — vary with "should be", "to make sure", "to confirm"
- ❌ Not referencing code entities with backticks
- ❌ Using "Oops" for verification failures — use "Actually" or "However"
- ❌ Not fixing issues same-turn (26.4% of verify turns should contain a fix)
- ❌ Waiting for verification results without predicting expected output first
