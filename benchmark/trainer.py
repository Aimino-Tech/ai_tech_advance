"""Auto-training loop: run scenarios → score → extract failures → generate skill patches → re-run.

Usage:
    python -m benchmark.trainer train --course deepseek-baseline --model deepseek-v4-flash
    python -m benchmark.trainer status
    python -m benchmark.trainer curriculum --course my-course
"""

import asyncio
import json
import os
import sqlite3
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Final

import click

from benchmark.eval import _get_db as _get_dojo_db
from benchmark.eval import _init_db as _init_dojo_db
from benchmark.eval import _load_course, _parse_scenarios
from benchmark.skill_generator import (
    SkillGenerator,
    load_traces_from_dir,
    save_skill_patch,
)
from benchmark.judge import JudgeModel
from benchmark.models import ScenarioResult
from benchmark.runner import AgentHarness, AgentError

_TRAINER_DB_DIR: Final = Path(__file__).resolve().parent / "db"
_TRAINER_DB_PATH: Final = _TRAINER_DB_DIR / "trainer.db"
_COURSES_DIR: Final = Path(__file__).resolve().parent.parent / "courses"
_SKILLS_DIR: Final = Path(__file__).resolve().parent.parent / "skills"
_TRACES_DIR: Final = Path(__file__).resolve().parent.parent / "traces"

_ENV_API_KEY: Final = "DOJO_API_KEY"


def _get_db() -> sqlite3.Connection:
    """Get a connection to the trainer SQLite database."""
    _TRAINER_DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_TRAINER_DB_PATH))
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def _init_trainer_db() -> None:
    """Initialize the trainer database schema."""
    conn = _get_db()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS training_runs (
                id TEXT PRIMARY KEY,
                course TEXT NOT NULL,
                model TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                total_iterations INTEGER,
                final_score REAL
            );

            CREATE TABLE IF NOT EXISTS training_iterations (
                id TEXT PRIMARY KEY,
                training_run_id TEXT NOT NULL REFERENCES training_runs(id),
                iteration INTEGER NOT NULL,
                score REAL NOT NULL,
                improvement REAL,
                skill_path TEXT,
                failure_count INTEGER,
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_ti_run
                ON training_iterations(training_run_id);
        """)
        conn.commit()
    finally:
        conn.close()


def _check_api_key() -> str:
    """Check DOJO_API_KEY is set, raise helpful error if not."""
    key = os.environ.get(_ENV_API_KEY, "")
    if not key:
        raise click.ClickException(
            f"{_ENV_API_KEY} is not set. "
            "Set it to your API key before running training.\n"
            f"  export {_ENV_API_KEY}=your-api-key-here"
        )
    return key


class TrainingLoop:
    """The auto-training loop: iterate eval → analyze → patch → re-eval."""

    def __init__(
        self,
        course: str,
        model: str,
        max_iterations: int = 10,
        target_score: float | None = None,
        judge_mode: str | None = None,
        judge_model: str | None = None,
    ) -> None:
        self.course = course
        self.model = model
        self.max_iterations = max_iterations
        self.target_score = target_score
        self.judge_mode = judge_mode
        self.judge_model = judge_model
        self.api_key = os.environ.get(_ENV_API_KEY, "")
        self.generator = SkillGenerator()
        self.run_id = str(uuid.uuid4())

    async def run(self) -> dict[str, Any]:
        """Execute the full training loop.

        Returns summary dict with training_run_id, iterations, final_score.
        """
        _check_api_key()
        _init_trainer_db()

        started_at = datetime.now(timezone.utc).isoformat()
        conn = _get_db()
        try:
            conn.execute(
                """INSERT INTO training_runs (id, course, model, started_at)
                   VALUES (?, ?, ?, ?)""",
                (self.run_id, self.course, self.model, started_at),
            )
            conn.commit()
        finally:
            conn.close()

        click.echo(f"\n{'='*60}")
        click.echo(f"Training Run: {self.run_id}")
        click.echo(f"Course:       {self.course}")
        click.echo(f"Model:        {self.model}")
        click.echo(f"Max Iters:    {self.max_iterations}")
        click.echo(f"Target:       {self.target_score or 'auto'}")
        click.echo(f"{'='*60}\n")

        prev_score = 0.0
        stall_count = 0
        best_score = 0.0
        current_skills: list[str] = []

        for iteration in range(1, self.max_iterations + 1):
            click.echo(f"\n{'─'*50}")
            click.echo(f"ITERATION {iteration}/{self.max_iterations}")
            click.echo(f"{'─'*50}")

            # 1. Run eval on current skill set
            score, failures = await self._run_eval(current_skills)

            improvement = score - prev_score
            click.echo(f"\n  Score:      {score:.2f}")
            click.echo(f"  Prev:       {prev_score:.2f}")
            click.echo(f"  Improvement: {improvement:+.2f}")
            click.echo(f"  Failures:   {len(failures)}")

            self._save_iteration(iteration, score, improvement, None, len(failures))

            # 2. Check termination conditions
            if self.target_score is not None and score >= self.target_score:
                click.echo(f"\n  ✓ Target score {self.target_score} reached!")
                self._finalize_run(iteration, score)
                return {
                    "training_run_id": self.run_id,
                    "iterations": iteration,
                    "final_score": score,
                    "reason": "target_score_reached",
                }

            if score > best_score:
                best_score = score

            if improvement < 0.02:
                stall_count += 1
                click.echo(f"  ⚠ Stall {stall_count}/2 (improvement < 2%)")
                if stall_count >= 2:
                    click.echo(f"\n  ■ Converged after {iteration} iterations (score: {score:.2f})")
                    self._finalize_run(iteration, score)
                    return {
                        "training_run_id": self.run_id,
                        "iterations": iteration,
                        "final_score": score,
                        "reason": "converged",
                    }
            else:
                stall_count = 0

            # 3. Extract failure patterns
            if not failures:
                click.echo("\n  No failures — model is perfect on this course!")
                self._finalize_run(iteration, score)
                return {
                    "training_run_id": self.run_id,
                    "iterations": iteration,
                    "final_score": score,
                    "reason": "no_failures",
                }

            patterns = self.generator.extract_failure_patterns(failures)
            click.echo(f"\n  Failure patterns detected: {len(patterns)}")
            for p in patterns:
                click.echo(f"    - {p['pattern']}: {p['count']} failures")

            # 4. Generate skill patch
            skill_name = f"auto-trained-{self.course}-iter{iteration}"
            skill_content = self.generator.generate_skill_patch(patterns, skill_name)
            skill_path = save_skill_patch(skill_content, iteration)
            click.echo(f"\n  ✓ Skill patch saved: {skill_path}")

            self._update_iteration_skill(iteration, str(skill_path))

            # 5. Load new skill for next iteration
            current_skills = [str(skill_path)]
            prev_score = score

            click.echo(f"\n  Next iteration will use skill: {skill_name}")

        # Max iterations reached
        self._finalize_run(self.max_iterations, prev_score)
        click.echo(f"\n  ■ Max iterations ({self.max_iterations}) reached.")
        return {
            "training_run_id": self.run_id,
            "iterations": self.max_iterations,
            "final_score": prev_score,
            "reason": "max_iterations",
        }

    async def _run_eval(
        self,
        skills: list[str],
    ) -> tuple[float, list[ScenarioResult]]:
        """Run a single evaluation pass and return (total_score, failures)."""
        import sqlite3 as _sqlite3

        _init_dojo_db()

        course_data = _load_course(self.course)
        scenarios = _parse_scenarios(course_data)

        if not scenarios:
            raise click.ClickException(f"Course '{self.course}' has no scenarios")

        harness = AgentHarness(model=self.model, api_key=self.api_key)
        judge = JudgeModel(
            mode=self.judge_mode,
            judge_model=self.judge_model,
            api_key=self.api_key,
        )

        total_score = 0.0
        failures: list[ScenarioResult] = []
        max_possible = sum(s.max_score for s in scenarios)

        for idx, scenario in enumerate(scenarios, 1):
            click.echo(f"  [{idx}/{len(scenarios)}] {scenario.name}... ", nl=False)

            try:
                output = await harness.invoke(scenario.prompt)
                verdict = await judge.grade(scenario, output)
                passed = bool(verdict["passed"])
                score = float(verdict["score"])
                feedback = str(verdict.get("feedback", ""))
                error: str | None = None
            except AgentError as e:
                output = ""
                passed = False
                score = 0.0
                feedback = ""
                error = str(e)

            result = ScenarioResult(
                scenario_id=scenario.id,
                passed=passed,
                score=score,
                output=output,
                judge_feedback=feedback,
                error=error,
                attempt=1,
            )

            total_score += result.score
            if not result.passed:
                failures.append(result)

            status = "PASS" if result.passed else "FAIL"
            click.echo(f"{status} ({result.score:.2f}/{scenario.max_score:.2f})")

        await harness.close()

        return total_score, failures

    def _save_iteration(
        self,
        iteration: int,
        score: float,
        improvement: float,
        skill_path: str | None,
        failure_count: int,
    ) -> None:
        """Record a training iteration in the DB."""
        conn = _get_db()
        try:
            conn.execute(
                """INSERT INTO training_iterations
                   (id, training_run_id, iteration, score, improvement,
                    skill_path, failure_count, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    str(uuid.uuid4()),
                    self.run_id,
                    iteration,
                    score,
                    improvement,
                    skill_path,
                    failure_count,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def _update_iteration_skill(self, iteration: int, skill_path: str) -> None:
        """Update the skill_path for a previously saved iteration."""
        conn = _get_db()
        try:
            conn.execute(
                "UPDATE training_iterations SET skill_path = ? WHERE training_run_id = ? AND iteration = ?",
                (skill_path, self.run_id, iteration),
            )
            conn.commit()
        finally:
            conn.close()

    def _finalize_run(self, total_iterations: int, final_score: float) -> None:
        """Mark the training run as completed."""
        conn = _get_db()
        try:
            conn.execute(
                """UPDATE training_runs
                   SET completed_at = ?, total_iterations = ?, final_score = ?
                   WHERE id = ?""",
                (
                    datetime.now(timezone.utc).isoformat(),
                    total_iterations,
                    final_score,
                    self.run_id,
                ),
            )
            conn.commit()
        finally:
            conn.close()


# --- CLI ---


@click.group()
def cli() -> None:
    """benchmark trainer — auto-training loop for skill improvement."""


@cli.command()
@click.option("--course", required=True, help="Course name (subdirectory under courses/)")
@click.option("--model", default=None, help="Model identifier (default: $DOJO_MODEL)")
@click.option("--iterations", default=10, type=int, help="Maximum training iterations (default: 10)")
@click.option("--target-score", default=None, type=float, help="Target score to stop at")
@click.option("--judge-mode", default=None, help="Judge mode: simple|llm (default: $DOJO_JUDGE_MODE)")
@click.option("--judge-model", default=None, help="Judge model (default: $DOJO_JUDGE_MODEL)")
def train(
    course: str,
    model: str | None,
    iterations: int,
    target_score: float | None,
    judge_mode: str | None,
    judge_model: str | None,
) -> None:
    """Run the auto-training loop: eval → analyze → patch → re-eval.

    Iteratively improves skills by running scenarios, extracting failure
    patterns, generating SKILL.md patches, and re-running until the
    target score is reached or convergence.
    """
    _check_api_key()

    resolved_model = model or os.environ.get("DOJO_MODEL", "deepseek-v4-flash")

    loop = TrainingLoop(
        course=course,
        model=resolved_model,
        max_iterations=iterations,
        target_score=target_score,
        judge_mode=judge_mode,
        judge_model=judge_model,
    )
    result = asyncio.run(loop.run())

    click.echo(f"\n{'='*60}")
    click.echo("TRAINING COMPLETE")
    click.echo(f"  Run ID:      {result['training_run_id']}")
    click.echo(f"  Iterations:  {result['iterations']}")
    click.echo(f"  Final Score: {result['final_score']:.2f}")
    click.echo(f"  Reason:      {result['reason']}")
    click.echo(f"{'='*60}")


@cli.command()
def status() -> None:
    """Show training status and results from all runs."""
    _init_trainer_db()
    conn = _get_db()
    try:
        # Summary
        run_count = conn.execute("SELECT COUNT(*) FROM training_runs").fetchone()[0]
        if run_count == 0:
            click.echo("No training runs yet.")
            click.echo("Start one with: python -m benchmark.trainer train --course <name> --model <model>")
            return

        click.echo(f"\nTraining runs: {run_count}\n")

        rows = conn.execute(
            """SELECT id, course, model, started_at, completed_at,
                      total_iterations, final_score
               FROM training_runs
               ORDER BY started_at DESC
               LIMIT 20"""
        ).fetchall()

        for row in rows:
            status_str = "✓ done" if row["completed_at"] else "⋯ running"
            score = row["final_score"] if row["final_score"] is not None else "—"
            iters = row["total_iterations"] if row["total_iterations"] is not None else "—"
            click.echo(f"  Run:     {row['id']}")
            click.echo(f"  Course:  {row['course']}")
            click.echo(f"  Model:   {row['model']}")
            click.echo(f"  Status:  {status_str}")
            click.echo(f"  Iters:   {iters}")
            click.echo(f"  Score:   {score}")
            click.echo(f"  Started: {row['started_at']}")
            if row["completed_at"]:
                click.echo(f"  Ended:   {row['completed_at']}")
            click.echo("")

            # Show iterations for completed runs
            if row["completed_at"]:
                iters_rows = conn.execute(
                    """SELECT iteration, score, improvement, failure_count, skill_path
                       FROM training_iterations
                       WHERE training_run_id = ?
                       ORDER BY iteration""",
                    (row["id"],),
                ).fetchall()

                if iters_rows:
                    click.echo("    Iterations:")
                    click.echo(f"    {'#':<5} {'Score':<8} {'Δ':<8} {'Failures':<10} Skill")
                    click.echo(f"    {'-'*60}")
                    for ir in iters_rows:
                        imp = f"{ir['improvement']:+.2f}" if ir['improvement'] is not None else " —"
                        skill = ir['skill_path'] or "—"
                        click.echo(
                            f"    {ir['iteration']:<5} {ir['score']:<8.2f} {imp:<8} "
                            f"{ir['failure_count']:<10} {skill}"
                        )
                    click.echo("")

    finally:
        conn.close()


@cli.command()
@click.option("--course", required=True, help="Course name for the generated curriculum")
@click.option("--traces-dir", default=None, help="Directory with Fable 5 traces (default: traces/)")
@click.option("--output", default=None, help="Output file path (default: courses/<name>/dojo.md)")
def curriculum(
    course: str,
    traces_dir: str | None,
    output: str | None,
) -> None:
    """Generate a curriculum (dojo.md course) from Fable 5 traces."""
    resolved_traces_dir = Path(traces_dir) if traces_dir else _TRACES_DIR

    if not resolved_traces_dir.exists():
        raise click.ClickException(
            f"Traces directory not found: {resolved_traces_dir}"
        )

    traces = load_traces_from_dir(resolved_traces_dir)
    if not traces:
        click.echo(f"No traces found in {resolved_traces_dir}.")
        return

    generator = SkillGenerator()
    content = generator.curriculum_from_traces(traces, course)

    if not content.strip():
        click.echo("No curriculum generated (traces may be empty or malformed).")
        return

    # Determine output path
    if output:
        out_path = Path(output)
    else:
        course_dir = _COURSES_DIR / course
        course_dir.mkdir(parents=True, exist_ok=True)
        out_path = course_dir / "dojo.md"

    out_path.write_text(content)
    click.echo(f"Curriculum written to {out_path}")
    click.echo(f"  Scenarios: {len(traces)}")
    click.echo(f"  Source:    {resolved_traces_dir}")


if __name__ == "__main__":
    cli()
