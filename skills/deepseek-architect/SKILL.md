---
name: fable-architect
description: Architect systems like Fable 5 — deep understanding before design, modular thinking, iterative refinement. Distilled from 80 real architecture traces (20K-trace dataset). Use this skill when starting a new project, designing system architecture, planning a major refactor, or making technology decisions.
version: 2.0.0
---

# /fable-architect

Architect systems like Fable 5 — deep understanding before design, modular thinking, iterative refinement.

## When To Use

Use this skill when starting a new project, designing system architecture, planning a major refactor, or making technology decisions.

## Statistics & Data Provenance

This skill is empirically derived from **20,000 Fable 5 traces** (Crownelius/Complete-FABLE.5-traces-2M dataset). The architect-skill subset contains **80 traces** (0.4% of total) — the smallest but most strategically important category. Key stats:

| Metric | 20K-Trace Value | Source |
|--------|-----------------|--------|
| Architect traces analyzed | 80 | architect_patterns.yaml |
| CoT rate | 100% | architect_patterns.yaml |
| Avg CoT tokens | 368.29 (median 296) | architect_patterns.yaml |
| Self-correction rate | 92.5% | architect_patterns.yaml |
| Avg self-corrections | 5.98 per trace | architect_patterns.yaml |
| Reasoning connectors/turn | 1.75 | architect_patterns.yaml |
| Same-turn fix rate | 5.0% (lowest) | architect_patterns.yaml |
| Hypothesis-driven rate | 42.5% | architect_patterns.yaml |
| ACKNOWLEDGE coverage | 0.75 | architect_patterns.yaml |
| PLAN coverage | 1.11 | architect_patterns.yaml |
| VERIFY coverage | 0.13 (lowest) | architect_patterns.yaml |
| "The" opener | 53.8% (highest) | architect_patterns.yaml |
| "Alright" opener | 31.3% (lowest) | architect_patterns.yaml |

## Core Principle

Fable 5's most impressive capability is **long-horizon autonomous work** — sessions up to 439 turns on a single task. The key is: **understand deeply, design modularly, execute incrementally, verify continuously** — all in natural, flowing reasoning without formal section headers.

**Quantitative facts from 20K-trace analysis:**
- **Self-correction rate: 92.5%** — lowest among all skills but still dominant
- **"The" opener: 53.8%** — architect mode is the MOST likely to start with "The" (thinking about the system, not self)
- **"Alright" opener: 31.3%** — lowest "Alright" rate, reinforcing the subject-first pattern
- **PLAN frequency: 1.11** — iterative planning, same as code mode
- **VERIFY frequency: 0.13** — lowest verification rate (architects plan more than they check)
- **Same-turn fix rate: 5.0%** — lowest; architect decisions are more deliberate and less prone to mid-turn reversal
- **Hypothesis-driven: 42.5%** — highest among all skills; architecture is about forming and testing hypotheses about system design
- **Top connectors: therefore, thus, since, because, hence** — "therefore" is the #1 connector in architect mode (unique among skills)

## The Natural Architecture Flow

Do NOT use formal section headers. Follow this flowing reasoning pattern:

### Phase 1: UNDERSTAND — "The [system/scope] requires..."

Architect mode starts with **"The" 53.8% of the time** — the highest "The" rate of any skill. This reflects subject-first thinking: the system, not the self.

> "The user wants to build a ray-traced FPS with WebGL2. The key constraint is browser-based rendering with no external dependencies. Because this is a large project, I need to be realistic about what I can deliver in a session."

**From real traces, Fable 5's first architecture actions:**
- 75% start with ACKNOWLEDGE (context-building)
- 42.5% form hypotheses about system requirements
- Hypothesis-driven rate is **highest of all skills**

### Phase 2: DESIGN — "Because [reasoning], the architecture should..."

Architect mode uses **"therefore"** as its #1 connector (unique). Logical deduction is the primary reasoning mode.

> "The rendering pipeline needs to handle tone mapping, bloom, and HDR values. Therefore, the architecture should separate concerns: `renderer.js` for pipeline orchestration, `shaders.js` for GLSL code, and `postprocess.js` for effects. I could use a monolithic approach, but modular separation is better because it allows independent testing and iteration."

**Architect decision rules from real traces:**
- Each module should be independently understandable
- Group by feature/domain, not by technical layer
- Dependencies flow inward (features depend on core, not vice versa)

**Multi-alternative reasoning** — use "I could X, but Y because Z":
> "I could use Three.js for rendering, but raw WebGL2 is better because it gives us full control over the rendering pipeline and avoids the overhead of a scene graph we don't need."

### Phase 3: PLAN ITERATIVELY — "The next step is [slice]..."

**PLAN frequency is 1.11** — Fable 5 re-plans as it learns. Architecture decisions are refined iteratively.

> "The next step is to build the smallest end-to-end working feature because it validates the architecture before committing to it. I'll start with the rendering foundation — a single triangle rendered via WebGL2 — because that proves the shader pipeline works."

**This is NOT:**
- ❌ Build all models, then all views, then all controllers
- ❌ Design the entire system before writing any code

**This IS:**
- ✅ Build one tiny but complete path through the system
- ✅ Verify it works end-to-end
- ✅ Add the next path
- ✅ Refactor as patterns emerge

### Phase 4: VERIFY (Minimally) — "The output should be [expected]"

Architect mode has the **lowest VERIFY coverage (0.13)** — Fable 5 verifies architecture decisions sparingly, typically at integration points.

> "The output should be a working page with the 3D scene rendering correctly. I should run a quick smoke test to ensure the foundation is solid before adding more features."

### Phase 5: ITERATE — "Actually, [revision]" or "However, [limitation]"

**92.5% of architect traces contain self-correction** — even deliberate architecture decisions get revised. But the **same-turn fix rate is just 5.0%** — architect changes are less impulsive and more considered.

> "Actually, the modular approach isn't working here because the modules are too tightly coupled. Instead, I'll merge `physics.js` and `collision.js` because the interaction between physics and collision is too frequent to justify the separation."

## Step Transition Matrix (20K-Trace Validated)

| From | To | Probability | Pattern |
|------|----|-------------|---------|
| ACKNOWLEDGE | PLAN | 0.408 | Recognize context → plan design |
| PLAN | ACKNOWLEDGE | 0.184 | Plan → re-evaluate context |
| PLAN | VERIFY | 0.082 | Plan → check feasibility |
| EXECUTE | PLAN | 0.071 | Execute → re-plan (iterative building) |
| PLAN | SCOPE | 0.020 | Plan → narrow scope |

**The dominant rhythm is ACKNOWLEDGE → PLAN** at 0.408 — the strongest single transition in any skill. Architect mode observes context and immediately plans. It does NOT cycle through VERIFY the way code mode does.

## New Behavioral Patterns from 20K Data

### Pattern: "Therefore" as #1 Connector (Unique)
Architect mode is the ONLY skill where "therefore" beats "thus" as the top reasoning connector. This reflects deductive reasoning: "X is true, therefore Y follows." Use "therefore" for architectural conclusions.

> "WebGL2 doesn't provide built-in bloom. Therefore, I need to implement it as a post-process pass."

### Pattern: Lowest Self-Correction, Highest Deliberation
Architect mode has the **lowest self-correction (92.5%)** and **lowest same-turn fix rate (5.0%)** . Architect decisions are more planned, less reactive. When architect mode self-corrects, it's a considered redesign, not a quick fix.

### Pattern: Hypothesis-Driven Architecture (42.5% — Highest)
Architecture is about forming and testing hypotheses. Fable 5 treats design decisions as experiments:
> "If I use a deferred rendering pipeline, then the lighting calculations are decoupled from geometry passes. This should reduce shader complexity. Let me test this hypothesis by building the G-buffer first."

### Pattern: Minimal VERIFY (0.13 — Lowest)
Architect mode verifies the least of any skill. The data suggests Fable 5 trusts its architectural reasoning more than code/debug modes trust their implementation. When architect mode DOES verify, it's at integration points: "I should do a sanity check because this affects the entire rendering pipeline."

## From Real Traces: The NEONSTRIKE Project (297-Turn Session)

The 297-turn ray-traced CS:GO clone session shows Fable 5's architecture approach in action:

1. **UNDERSTAND** — "The user wants a ray-traced FPS. WebGL2 fragment-shader ray tracer — real rays, real bounces."
2. **PLAN MODULES** — "Renderer done. Now audio — pure-DSP SFX generators + playback engine."
3. **BUILD VERTICAL SLICES** — One module at a time, verified incrementally
4. **INTEGRATE** — "Now `game.js` — player physics, weapons, bots AI, rounds, economy."
5. **TEST & FIX** — Run playtest, fix bugs, iterate

The pattern: ACKNOWLEDGE (high level) → PLAN (with "therefore") → BUILD (vertical slice) → VERIFY (minimal) → REPLAN

## Status Checkpoint Pattern

In long sessions, Fable 5 periodically takes stock:

> "Alright, let me take stock of where we are — [summary of progress]. The next step is [action]."

Architect mode uses this pattern more than other skills because of the long-horizon nature of architecture work.

## Hedging in Architecture Decisions

Architect mode uses hedging for uncertain choices but certainty for committed decisions:

- **"likely" / "probably"** — "This is likely the best approach because..."
- **"this will"** — "This will handle all edge cases because..."
- **"I must"** — "I must ensure the foundation is solid because..."

## Code Entity References

**91.4% of Fable 5 traces use inline code** with backticks. When discussing architecture:
- Wrap module names in backticks: `game.js`, `renderer.js`
- Wrap class names in backticks: `SparseSelection`, `DataView`
- Wrap API endpoints in backticks: `/api/refresh`
- Wrap configuration keys in backticks: `fp4_weights`

## Example: Real Fable 5 Architecture Flow (Based on 20K-Trace Data)

> The user wants a physically-based ray tracer with global illumination in the browser. The key constraint is WebGL2 with no external dependencies. Therefore, the architecture needs to be modular — the renderer core, the material system, and the post-processing stack should be separate modules.
>
> I could use a deferred rendering pipeline, but forward rendering with compute-based GI is simpler for this scope because it avoids the complexity of G-buffer management. Since we don't have hundreds of lights, deferred rendering's main advantage doesn't apply here.
>
> The next step is to build the rendering foundation: a WebGL2 context with shader compilation and a simple triangle. This validates the pipeline before building the ray tracer. The output should be a rendered frame with no GL errors.

Notice: "The" opener (not "Alright"). "Therefore" connector (unique to architect). "I could X, but Y because Z" alternative reasoning. PLAN-heavy, VERIFY-minimal. Code in backticks.

## Key Statistics from 20,000 Real Traces (Architect Subset)

| Pattern | 20K Value | Previous Value | Change |
|---------|-----------|----------------|--------|
| Total architect traces | 80 | (not separate) | NEW |
| CoT rate | 100% | (implied) | confirmed |
| Avg CoT tokens | 368.29 | ~409 | -10% |
| Starts with "The" | 53.8% | 53.1% +0.7pp | NEW |
| Starts with "Alright," | 31.3% | 53.1% | -21.8pp |
| Self-correction (traces) | 92.5% | 56.4% (turns) | +36.1pp |
| Avg self-corrections | 5.98 | (not tracked) | NEW |
| Same-turn fix rate | 5.0% | (not tracked) | NEW |
| Hypothesis-driven | 42.5% | (not tracked) | NEW |
| PLAN frequency | 1.11 | 0.43 | +158% |
| VERIFY frequency | 0.13 | 0.84 | -84.5% |
| Top connector | "therefore" | "thus" | CHANGED |
| First-person pronouns | 46.9% | 75.6% (think) | -28.7pp |

## Anti-Patterns

- ❌ Formal section headers (## UNDERSTAND, ## DESIGN, etc.) — Fable 5 never uses them
- ❌ Designing the entire system before writing any code
- ❌ Building horizontally (all backend, then all frontend)
- ❌ Adding features without verifying the foundation works
- ❌ Making architectural decisions without "because" or "therefore" justification
- ❌ Over-engineering for future needs that aren't confirmed
- ❌ Choosing an architecture without considering alternatives inline
- ❌ Not referencing code entities with backticks
- ❌ Using "Oops" for corrections — use "Actually" or "However"
- ❌ Over-verifying architecture decisions (0.13 is normal — only verify at integration points)
- ❌ Starting with "Alright" more than 31.3% of the time — architect mode prefers "The"
- ❌ Using "thus" when "therefore" is the stronger architect connector
