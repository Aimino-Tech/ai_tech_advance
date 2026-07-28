---
name: fable-debug
description: Debug like Fable 5 — systematic root cause analysis. Distilled from 4,665 real traces.
---

# /fable-debug

## Debug Loop
1. **Observe** — what exactly is happening vs what should happen
2. **Investigate** — gather evidence: logs, error messages, state
3. **Hypothesize** — form a theory about root cause. List ALL possibilities
4. **Verify hypothesis** — test your theory with a targeted action
5. **Root cause confirmed?** → Fix. Otherwise → back to step 2.

## Rules
- Read the code before assuming you know the bug
- Look at the ACTUAL error message, not what you expect it to say
- Form ≥2 competing hypotheses before committing to one
- The true root cause must explain ALL symptoms, not just one
- After fix, verify the bug is actually gone
- 56% of Fable 5 debug turns contain self-correction — adjusting based on new evidence is normal
- "Actually" and "However" are the top correction markers (not "Oops")

## Anti-Patterns
- Don't fix by intuition — gather evidence first
- Don't fix a symptom while ignoring the root cause
- Don't change code you haven't read
- Don't shotgun debug (changing things randomly hoping something works)
- Don't skip verification after the fix
