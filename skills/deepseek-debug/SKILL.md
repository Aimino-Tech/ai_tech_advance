---
name: fable-debug
description: Debug like Fable 5 — systematic root cause analysis with natural reasoning flow. Distilled from 190 real debug traces (20K-trace dataset). Use this skill when you encounter an error, unexpected behavior, failing tests, or anything that does not work as intended.
version: 2.0.0
---

# /fable-debug

Debug like Fable 5 — systematic root cause analysis with natural reasoning flow.

## When To Use

Use this skill when you encounter an error, unexpected behavior, failing tests, or anything that doesn't work as intended.

## Statistics & Data Provenance

This skill is empirically derived from **20,000 Fable 5 traces** (Crownelius/Complete-FABLE.5-traces-2M dataset). The debug-skill subset contains **190 traces** (0.95% of total). Key stats:

| Metric | 20K-Trace Value | Source |
|--------|-----------------|--------|
| Debug traces analyzed | 190 | debug_patterns.yaml |
| CoT rate | 100% | debug_patterns.yaml |
| Avg CoT tokens | 402.85 (median 374) | debug_patterns.yaml |
| Self-correction rate | 99.47% | debug_patterns.yaml |
| Avg self-corrections | 6.92 per trace | debug_patterns.yaml |
| Reasoning connectors/turn | 2.19 | debug_patterns.yaml |
| Same-turn fix rate | 19.5% | debug_patterns.yaml |
| Hypothesis-driven rate | 36.3% | debug_patterns.yaml |
| ACKNOWLEDGE coverage | 0.84 | debug_patterns.yaml |
| SCOPE coverage | 0.24 (highest of all skills) | debug_patterns.yaml |
| PLAN coverage | 1.24 (highest of all skills) | debug_patterns.yaml |
| VERIFY coverage | 0.53 | debug_patterns.yaml |
| "Alright" opener | 47.4% | debug_patterns.yaml |

## Core Principle

Fable 5 doesn't guess — it **investigates methodically** with flowing, natural reasoning. Debug mode has the **highest self-correction rate (99.47%)** of any Fable 5 skill — debugging IS self-correction. From 190 real debug traces:

**Quantitative facts from 20K-trace analysis:**
- **99.47%** of debug traces contain self-correction — near universal
- **6.92 avg self-corrections** — highest count of any skill
- **2.19 reasoning connectors per turn** — highest connector density
- **1.24 PLAN steps per trace** — most iterative planning
- **0.24 SCOPE coverage** — highest scoping rate (debug requires understanding boundaries)
- **36.3% hypothesis-driven** — forms and tests hypotheses
- **19.5% same-turn fix rate** — catches and fixes within the same reasoning turn
- **"Alright" opener:** 47.4% (slightly less than code but still dominant)
- **Edit→Bash(verify)** is the #1 debug loop pattern
- **Data from code tool use (3,203 traces):** Edit→Bash count 229, Bash→Bash 765

## The Natural Debugging Flow

Do NOT use formal section headers. Follow this flowing reasoning pattern:

### Step 1: OBSERVE — "Alright, the [error/behavior] shows..."

State exactly what went wrong. Be precise about the failure.

> "Alright, the latest test run failed with `TypeError: buf.readUInt32BE is not a function`. The stack trace points to line 8 in `test/png.mjs`. The error tells me that `buf` is not a Node `Buffer` object because `Uint8Array` doesn't have `readUInt32BE`."

**What to include:**
- The exact error message in backticks (not paraphrased) — 91.4% of traces use backtick code references
- The exact conditions when it occurs
- What WORKS vs what DOESN'T
- Your immediate analysis of what the error means with "because"

### Step 2: INVESTIGATE / SCOPE — "I need to understand [what]..."

Debug mode has the **highest SCOPE coverage (0.24)** of any skill — Fable 5 scopes the problem before diving in.

> "I need to understand what `buf` actually is at runtime. I'll read `test/png.mjs` because the stack trace points there. I should also check how `buf` is created because the root cause might be upstream."

**Investigation vocabulary from real traces:**
- "diagnose" — 148 occurrences
- "investigate" — 100 occurrences
- "debug" — 312 occurrences
- "error message" — 187 occurrences
- "stack trace" — 39 occurrences
- "traceback" — 111 occurrences

### Step 3: HYPOTHESIZE — "Because [evidence], the issue is likely..."

**36.3% of debug traces are hypothesis-driven** — Fable 5 forms specific, testable hypotheses.

> "Because `buf` comes from Puppeteer's screenshot API which returns `Uint8Array`, the issue is likely a type mismatch. It could also be that the `Buffer` polyfill isn't loaded, but the type mismatch is more likely because the error specifically says `readUInt32BE is not a function` — that's a method that exists on `Buffer` but not `Uint8Array`."

**Rules:**
- Generate specific, testable hypotheses
- Rank by likelihood with "because" reasoning
- Use hedging: "likely" (1.22/CoT), "perhaps", "probably"
- Don't fix yet — just hypothesize
- Consider: type mismatches, missing dependencies, logic errors, timing issues

### Step 4: IDENTIFY ROOT CAUSE — "The root cause is [X] because [Y]"

> "The root cause is that Puppeteer returns `Uint8Array` while the code assumes `Buffer`. The `readUInt32BE` call is just a symptom of the underlying type mismatch. Since both types wrap `ArrayBuffer`, the fix is straightforward — use `DataView` which works on both."

**Rules:**
- Distinguish symptoms from causes
- If root cause is in a different file/module than the error, say so
- Explain the chain: cause → intermediate effect → observed error

### Step 5: FIX — "The next step is to fix [X] by [action] because [reasoning]"

> "The next step is to replace the `Buffer` method calls with `DataView` equivalents because `DataView` works on any `ArrayBuffer` view. Because I only want to replace this specific occurrence, I'll target just the `readUInt32BE` call and the subsequent `readUInt32BE` calls. This should not affect other parts of the code because the rest of the module doesn't depend on `Buffer` methods."

**Rules:**
- Fix the ROOT CAUSE, not the symptom
- Make the MINIMAL change that fixes the problem
- Always justify with "because"
- Use precision edit justification: "because I only want to replace this specific occurrence"

### Step 6: VERIFY — "The output should be [expected] to ensure the fix works"

> "The output should be a successful PNG validation with no `TypeError`. I should verify by re-running the playtest to ensure the fix works correctly. If the error persists, I'll need to check whether there are other `Buffer` method calls in the file because they might also fail with `Uint8Array` input."

**Verification phrases from 20K data:**
- "should be" (27.5%)
- "to verify" (21.0%)
- "to ensure" (16.5%)
- "to confirm" (14.3%)
- "to make sure" (9.4%)

## Self-Correction During Debugging

**99.47% of debug traces contain self-correction** — the highest of any skill. **19.5% involve same-turn fixes.** Debugging IS self-correction.

> "Actually, I was looking at the wrong file. The actual issue is in `[correct file]` because the error stack trace clearly shows the failure there."
> "However, the fix I applied didn't address the root cause — it only fixed the symptom. The real issue is `[deeper problem]` because `[evidence]`."

**Correction markers from 20K data:**
- "Actually, [correction]" — 32.4% of CoTs
- "However, [contradiction]" — 23.0% of CoTs
- "Wait, [realization]" — 8.5% of CoTs
- "Instead, [alternative]" — 9.6% of CoTs

And corrections **continue forward 74.4%** of the time.

## Step Transition Matrix (20K-Trace Validated)

| From | To | Probability | Pattern |
|------|----|-------------|---------|
| ACKNOWLEDGE | PLAN | 0.201 | Recognize issue → plan approach |
| VERIFY | PLAN | 0.123 | Verify failed → re-plan fix |
| PLAN | VERIFY | 0.116 | Plan approach → verify it works |
| PLAN | ACKNOWLEDGE | 0.070 | Plan → re-assess context |
| PLAN | SCOPE | 0.044 | Plan → narrow scope of investigation |
| SCOPE | PLAN | 0.048 | Narrow scope → specific plan |

Debug mode has the **highest SCOPE→PLAN transition (0.048)** — the most scoping activity of any skill.

## New Behavioral Patterns from 20K Data

### Pattern: Highest Self-Correction Density (6.92 per trace)
Debug mode has the **highest average self-corrections** of any Fable 5 skill at 6.92 per trace. This reflects the inherently iterative nature of debugging — each hypothesis tested, each fix verified, each failure triggering a new correction cycle. Fable 5's debug traces are a chain of "try → fail → correct → re-try."

### Pattern: PLAN-Heavy Iteration (1.24 per trace)
Debug mode has the **highest PLAN frequency** (1.24) — the most iterative planning of any skill. Debug is not "plan once, execute, done." It's a constant cycle of: test a hypothesis → observe result → plan next step → test again.

### Pattern: SCOPE Before INVESTIGATE (0.24 coverage)
Debug mode is the only skill with significant SCOPE coverage (0.24 vs. 0.09 for code, 0.08 for verify, 0.06 for architect). Fable 5 scopes the problem before investigating: "Is the issue in module A or B?" This scoping-first approach saves time by narrowing the search space.

### Pattern: HIGHEST Reasoning Connector Density (2.19/turn)
Debug reasoning uses more logical connectors than any other skill. Each debugging step connects to the previous with "because/since/therefore/thus/given that":
> "The error is X because Y. Since A is true, the root cause must be B. Therefore, I should fix C."

## Common Debug Patterns from Real Traces

### Pattern: Type Mismatch
> "Alright, the error is `TypeError: buf.readUInt32BE is not a function`. That tells me that `buf` is not a Node `Buffer` object — Puppeteer returns `Uint8Array`, not `Buffer`. Because `Uint8Array` doesn't have `readUInt32BE`, I need to use `DataView` instead."

### Pattern: Missing Dependency
> "The error says `Cannot find package 'puppeteer'`. I need to install it because the project requires it for screenshot capture. I'll run `npm install` to ensure the dependency is available."

### Pattern: Logic Error
> "The playtest is still failing the 'hitscan damages bot at close range' check. The log shows the player is at `[position]` while the bot is at `[position]`. Because the hit detection uses a forward vector that points almost directly toward the bot yet the hit result is false, the issue is likely in the ray-box intersection code."

### Pattern: Async/Timing Issue
> "The test works sometimes but fails sometimes. Because the failure is intermittent, this is likely a race condition — `[component A]` hasn't finished `[action]` before `[component B]` tries to read it. I must add proper async handling because the current code doesn't await the promise."

## Code Entity References

**91.4% of Fable 5 traces use inline code** with backticks. When debugging:
- Always wrap error messages in backticks
- Always wrap function/method names in backticks
- Always wrap file paths in backticks
- Always wrap variable names in backticks

## Example: Real Fable 5 Debug Flow (Based on 20K-Trace Data)

> Alright, the recent series of edits to `renderer.js` should have addressed the black-box artifact that only showed up when the graphics preset was set to ultra (1280×720). I added a safeguard against near-zero `a` in the ray-sphere intersection, inserted NaN checks and clamping for the final fragment color, and also did the same for the bloom pass shader.
>
> Now I need to confirm that these fixes actually eliminate the black box. Because the most straightforward way to verify is to re-run the exact test script, I'll issue a Bash command to run the playtest again. The output should show the black box gone in the screenshots because the NaN clamping should prevent the shader from producing invalid color values.
>
> If the black box persists, I'll need to dig deeper into the shader because the issue might be in a different code path — perhaps the tone mapping or the final output stage rather than the ray-sphere intersection.

Notice: "Alright" opener. "Because" connecting analysis. "Now I need to confirm" for verification. "Should" for expected outcome. Fallback plan included. Code in backticks.

## Key Statistics from 20,000 Real Traces (Debug Subset)

| Pattern | 20K Value | Previous Value | Change |
|---------|-----------|----------------|--------|
| Total debug traces | 190 | (not separate) | NEW |
| CoT rate | 100% | (implied) | confirmed |
| Avg CoT tokens | 402.85 | ~409 | -1.5% |
| Starts with "Alright," | 47.4% | 53.1% (think) | -5.7pp |
| Self-correction (traces) | 99.47% | 56.4% (turns) | +43.1pp |
| Avg self-corrections | 6.92 | (not tracked) | NEW |
| Same-turn fix rate | 19.5% | 37.4% (stated) | -17.9pp |
| Hypothesis-driven rate | 36.3% | ~30% | +6.3pp |
| PLAN frequency | 1.24 | 0.43 | +188% |
| SCOPE frequency | 0.24 | (not tracked) | NEW |
| VERIFY frequency | 0.53 | 0.84 | -36.9% |
| Reasoning connectors/turn | 2.19 | 2.14 | +2.3% |

## Anti-Patterns

- ❌ Formal section headers (## OBSERVE, ## HYPOTHESIZE, etc.) — Fable 5 never uses them
- ❌ Fixing symptoms without understanding root cause
- ❌ Making multiple changes simultaneously during debugging
- ❌ Assuming the first hypothesis is correct without verifying
- ❌ Skipping verification after the fix
- ❌ Adding print statements everywhere without a hypothesis
- ❌ Not using "because" to justify your debugging decisions
- ❌ Using "Oops" for self-correction — use "Actually" or "However"
- ❌ Not referencing code entities with backticks
- ❌ Going backward on corrections — 74.4% continue forward instead
- ❌ Not scoping the problem before investigating (debug SCOPE rate is 0.24 — highest of any skill)
- ❌ Making one plan and sticking to it — debug requires iterative re-planning (PLAN 1.24)
