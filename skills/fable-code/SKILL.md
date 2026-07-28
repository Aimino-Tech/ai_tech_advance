---
name: fable-code
description: Code like Fable 5 — methodical, verified, and deeply informed by context. Distilled from 4,665 real traces.
---

# /fable-code

## Core Loop
1. **Read first** — understand existing code before writing
2. **Plan structure** — outline approach before implementing
3. **Write code** — handle edge cases, not just the happy path
4. **Verify** — test or validate after every change
5. **Iterate** — fix issues found during verification

## Rules
- Read the file you're editing before changing it
- Match existing code style and patterns
- Handle edge cases: null/undefined, empty arrays, type mismatches
- Extract helpers at 2+ repetitions; inline single-use
- After edit, verify the output (build/test/read back)
- If something seems wrong, read the actual file — don't guess
- The most common Fable tool loop: Edit → Bash(verify) (229 occurrences in 4,665 traces)

## Anti-Patterns
- Don't write code without reading the surrounding context first
- Don't skip edge cases
- Don't use `as any` or `@ts-ignore`
- Don't leave TODO stubs or placeholder code
- Don't refactor unrelated code while fixing a bug
