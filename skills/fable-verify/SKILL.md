---
name: fable-verify
description: Verify like Fable 5 — systematic quality assurance woven into reasoning. Distilled from 4,665 real traces.
---

# /fable-verify

## Verification Flow
Verification is INLINE — woven into reasoning, not a separate phase. Each action should predict an expected outcome:
> "The output should be a clean build with no errors."

## Checkpoints
- Before acting: "The output should be [expected]"
- After acting: did the actual match the expected?
- If mismatch → investigate, don't ignore

## What to Verify
- Correctness: does the output match requirements?
- Edge cases: what happens at boundaries?
- Regressions: does existing behavior still work?
- Errors: are failures handled gracefully?

## Key Phrases from Fable 5 Traces
- "should be" — 27.5% of traces
- "to verify" — 21.0%
- "to ensure" — 16.5%
- "to confirm" — 14.3%
- "to make sure" — 9.4%

## Anti-Patterns
- Don't skip verification because the change is "too small"
- Don't assume it works without checking
- Don't verify only the happy path
- Don't ignore unexpected output
