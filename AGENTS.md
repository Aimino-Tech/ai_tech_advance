# ai_tech_advance — Agent Instructions

## What this is

Prompt-layer knowledge distillation from frontier models (Claude Fable 5) to cheaper models (DeepSeek V4 Flash). No fine-tuning. Pure SKILL.md injection at inference time.

## The loop

1. Extract reasoning patterns from Fable 5 traces
2. Distill into SKILL.md files
3. Inject into DeepSeek V4 Flash
4. Score on dojo.md courses
5. Refine based on failure patterns
6. Repeat

## Skills (SKILL.md)

- `skills/deepseek-think/` — Per-turn reasoning: acknowledge → observe → execute → verify
- `skills/deepseek-code/` — Code generation with edge-case handling
- `skills/deepseek-debug/` — Root cause analysis and fix
- `skills/deepseek-architect/` — System decomposition and design
- `skills/deepseek-verify/` — Self-verification and test generation

## Scoring

- `benchmark/eval.py run --course <name> --model <model>` — run scenarios
- `benchmark/report.py dashboard` — generate trend chart
- Results stored in `benchmark/db/dojo.db` (git-committed SQLite)

## Courses

- `courses/deepseek-baseline/` — 10 smoke scenarios
- More courses added as the project matures

## CI

- `baseline.yml` — runs on push/PR to main
- `auto-train.yml` — nightly auto-training loop
- `report.yml` — trend report generation
