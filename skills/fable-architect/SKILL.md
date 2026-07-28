---
name: fable-architect
description: Architect like Fable 5 — deep understanding before design, modular thinking. Distilled from 4,665 real traces.
---

# /fable-architect

## Architecture Loop
1. **Understand requirements** — what problem are we solving?
2. **Decompose** — split into independent modules with clear interfaces
3. **Design vertical slice** — one complete path end-to-end before expanding
4. **Verify interfaces** — does each module have one clear purpose?
5. **Iterate** — refine boundaries based on what doesn't fit

## Rules
- Each module should answer: what does it do, how do you use it, what does it depend on?
- Can someone understand a unit without reading its internals? If not, the boundary is wrong.
- Can you change internals without breaking consumers? If not, the boundary is wrong.
- Prefer existing patterns over new abstractions
- Files growing large = doing too much. Split.
- Independent pieces should be independently testable

## Anti-Patterns
- Don't design without understanding the problem first
- Don't add abstractions before you have 3+ examples
- Don't create modules with tangled dependencies
- Don't over-engineer for "future needs" that aren't specified
- Don't skip writing down the design decisions and trade-offs
