#!/usr/bin/env bash
# evaluate_all.sh — Run baseline + skills-injected eval across all 6 courses
#
# Usage:
#   ./benchmark/evaluate_all.sh                    # run all with defaults (1 run each)
#   DOJO_API_KEY=sk-... ./benchmark/evaluate_all.sh
#   DOJO_API_KEY=sk-... ./benchmark/evaluate_all.sh --num-runs 3
#
# Set DOJO_API_KEY or the script will skip API-dependent commands.

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NUM_RUNS="${1:-1}"
COURSES="deepseek-baseline deepseek-think deepseek-code deepseek-debug deepseek-architect deepseek-verify"
RESULTS_DIR="$ROOT/benchmark/results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$RESULTS_DIR"

if [ -z "${DOJO_API_KEY:-}" ]; then
    echo "WARNING: DOJO_API_KEY not set. Running with --judge-mode simple (no API calls)."
    echo "Set DOJO_API_KEY to run actual model evaluations."
    echo ""
fi

echo "=============================================="
echo " Wave 4: Full Evaluation Pipeline"
echo " Courses:      $COURSES"
echo " Num Runs:     $NUM_RUNS"
echo " Timestamp:    $TIMESTAMP"
echo " DOJO_API_KEY: ${DOJO_API_KEY:+set}"
echo "=============================================="
echo ""

BASELINE_RUNS=()
SKILLS_RUNS=()

# ── Step 1: Baseline (no skills) ──
echo "══════════════════════════════════════════════"
echo " STEP 1: Baseline (no skills)"
echo "══════════════════════════════════════════════"
for course in $COURSES; do
    echo ""
    echo "--- Baseline: $course ---"
    cd "$ROOT"
    python3 -m benchmark.eval run \
        --course "$course" \
        ${DOJO_API_KEY:+--model deepseek-v4-flash} \
        --num-runs "$NUM_RUNS" \
        --judge-mode simple \
        2>&1 | tee "$RESULTS_DIR/baseline-${course}-${TIMESTAMP}.log" || true
done

echo ""
echo "══════════════════════════════════════════════"
echo " STEP 2: With Skills Injected"
echo "══════════════════════════════════════════════"
for course in $COURSES; do
    skill_name="${course#deepseek-}"
    # Only inject the matching skill for this course
    if [ "$course" = "deepseek-baseline" ]; then
        skill_arg="deepseek-think,deepseek-code,deepseek-debug,deepseek-architect,deepseek-verify"
    else
        skill_arg="$skill_name"
    fi
    echo ""
    echo "--- Skills: $course (skill: $skill_arg) ---"
    cd "$ROOT"
    python3 -m benchmark.eval run \
        --course "$course" \
        ${DOJO_API_KEY:+--model deepseek-v4-flash} \
        --skills "$skill_arg" \
        --num-runs "$NUM_RUNS" \
        --judge-mode simple \
        2>&1 | tee "$RESULTS_DIR/skills-${course}-${TIMESTAMP}.log" || true
done

# ── Step 3: Generate dashboard report ──
echo ""
echo "══════════════════════════════════════════════"
echo " STEP 3: Generate Reports"
echo "══════════════════════════════════════════════"
cd "$ROOT"
python3 -m benchmark.report dashboard --output "$RESULTS_DIR/dashboard-${TIMESTAMP}.html" 2>&1 || true
echo "Dashboard: $RESULTS_DIR/dashboard-${TIMESTAMP}.html"

# Compare baseline vs skills for each course if we have both
for course in $COURSES; do
    # Find baseline and skills run IDs from the logs
    baseline_run=$(grep -oP 'Run ID: \K[0-9a-f-]+' "$RESULTS_DIR/baseline-${course}-${TIMESTAMP}.log" 2>/dev/null | tail -1 || true)
    skills_run=$(grep -oP 'Run ID: \K[0-9a-f-]+' "$RESULTS_DIR/skills-${course}-${TIMESTAMP}.log" 2>/dev/null | tail -1 || true)
    if [ -n "$baseline_run" ] && [ -n "$skills_run" ]; then
        python3 -m benchmark.report compare \
            --run-a "$baseline_run" \
            --run-b "$skills_run" \
            --output "$RESULTS_DIR/compare-${course}-${TIMESTAMP}.html" 2>&1 || true
        echo "Comparison ($course): $RESULTS_DIR/compare-${course}-${TIMESTAMP}.html"
    fi
done

# ── Step 4: Run auto-training (if API key set) ──
if [ -n "${DOJO_API_KEY:-}" ]; then
    echo ""
    echo "══════════════════════════════════════════════"
    echo " STEP 4: Auto-Training (deepseek-code)"
    echo "══════════════════════════════════════════════"
    cd "$ROOT"
    python3 -m benchmark.trainer train \
        --course deepseek-code \
        --model deepseek-v4-flash \
        --iterations 5 \
        --target-score 90 2>&1 | tee "$RESULTS_DIR/train-${TIMESTAMP}.log" || true
else
    echo ""
    echo "══════════════════════════════════════════════"
    echo " STEP 4: Auto-Training skipped (no API key)"
    echo "══════════════════════════════════════════════"
fi

echo ""
echo "=============================================="
echo " Evaluation Complete"
echo " Results: $RESULTS_DIR"
echo "=============================================="
