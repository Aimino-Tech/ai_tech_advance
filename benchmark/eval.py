"""CLI for running evaluation courses and inspecting results."""

import asyncio
import json
import os
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any, Final

import click
import yaml

from benchmark.judge import JudgeModel
from benchmark.models import Scenario, ScenarioResult
from benchmark.runner import AgentHarness, AgentError

_DB_DIR: Final = Path(__file__).resolve().parent / "db"
_DB_PATH: Final = _DB_DIR / "dojo.db"
_COURSES_DIR: Final = Path(__file__).resolve().parent.parent / "courses"
_SCHEMA_PATH: Final = Path(__file__).resolve().parent / "schema.sql"

_PROJECT_ROOT: Final = Path(__file__).resolve().parent.parent


def _get_db() -> "sqlite3.Connection":
    """Get a SQLite connection with WAL mode and foreign keys enabled."""
    import sqlite3

    _DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB_PATH))
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def _init_db() -> None:
    """Initialize the database schema if not yet created."""
    import sqlite3

    conn = _get_db()
    try:
        schema = _SCHEMA_PATH.read_text()
        conn.executescript(schema)
        conn.commit()
    finally:
        conn.close()


def _get_git_sha() -> str | None:
    """Return the current git SHA, or None if not in a git repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=str(_PROJECT_ROOT),
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except (subprocess.SubprocessError, FileNotFoundError):
        return None


def _load_course(course_name: str) -> dict[str, Any]:
    """Load course definition from courses/<name>/dojo.md YAML."""
    course_path = _COURSES_DIR / course_name / "dojo.md"
    if not course_path.exists():
        # Also check for .yaml extension
        alt_path = _COURSES_DIR / course_name / "dojo.yaml"
        if alt_path.exists():
            course_path = alt_path
        else:
            raise click.ClickException(
                f"Course not found: {course_name} "
                f"(checked {course_path} and {alt_path})"
            )
    try:
        raw = course_path.read_text()
        raw = raw.strip()
        if raw.startswith("---"):
            raw = raw[3:].strip()
        if raw.endswith("---"):
            raw = raw[:-3].strip()
        data: dict[str, Any] = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        raise click.ClickException(f"Failed to parse course YAML: {e}") from e

    if not isinstance(data, dict) or "scenarios" not in data:
        raise click.ClickException(
            f"Course file {course_path} must contain a 'scenarios' key"
        )
    return data


def _parse_scenarios(data: dict[str, Any]) -> list[Scenario]:
    """Parse scenario dicts from course YAML into Scenario models."""
    scenarios: list[Scenario] = []
    for i, raw in enumerate(data["scenarios"]):
        if not isinstance(raw, dict):
            raise click.ClickException(f"Scenario at index {i} must be a dict")
        try:
            scenario = Scenario(
                id=str(raw["id"]),
                name=str(raw["name"]),
                description=str(raw.get("description", "")),
                difficulty=str(raw.get("difficulty", "smoke")),
                tags=list(raw.get("tags", [])),
                max_score=float(raw.get("max_score", 1.0)),
                prompt=str(raw["prompt"]),
                expected_behaviors=list(raw.get("expected_behaviors", [])),
                judge_criteria=list(raw.get("judge_criteria", [])),
            )
        except KeyError as e:
            raise click.ClickException(
                f"Scenario at index {i} is missing required field: {e}"
            ) from e
        except (TypeError, ValueError) as e:
            raise click.ClickException(
                f"Scenario at index {i} has invalid data: {e}"
            ) from e
        scenarios.append(scenario)
    return scenarios


def _upsert_scenarios(conn: "sqlite3.Connection", course: str, scenarios: list[Scenario]) -> None:
    """Insert or ignore scenario definitions."""
    for s in scenarios:
        conn.execute(
            """INSERT OR IGNORE INTO scenarios (id, course, name, description, difficulty, tags, max_score)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                s.id,
                course,
                s.name,
                s.description,
                s.difficulty,
                json.dumps(s.tags),
                s.max_score,
            ),
        )


async def _run_course(
    course_name: str,
    model: str,
    skills: list[str],
    judge_mode: str | None,
    judge_model: str | None,
) -> dict[str, Any]:
    """Execute all scenarios in a course and return results."""
    import sqlite3

    _init_db()

    course_data = _load_course(course_name)
    scenarios = _parse_scenarios(course_data)

    if not scenarios:
        msg = f"Course '{course_name}' has no scenarios"
        raise click.ClickException(msg)

    run_id = str(uuid.uuid4())

    harness = AgentHarness(model=model)
    resolved_model = harness.model

    click.echo(f"Run {run_id}: {len(scenarios)} scenarios on {resolved_model}")

    judge = JudgeModel(mode=judge_mode, judge_model=judge_model)
    git_sha = _get_git_sha()

    results: list[ScenarioResult] = []
    run_start = time.monotonic()

    async def run_one(scenario: Scenario) -> tuple[str, ScenarioResult]:
        """Run a single scenario and return (name, result)."""
        scenario_error: str | None = None
        try:
            output = await harness.invoke(scenario.prompt)
            verdict = await judge.grade(scenario, output)
            return scenario.name, ScenarioResult(
                scenario_id=scenario.id,
                passed=bool(verdict["passed"]),
                score=float(verdict["score"]),
                output=output,
                judge_feedback=verdict["feedback"],
                error=None,
                attempt=1,
            )
        except AgentError as e:
            return scenario.name, ScenarioResult(
                scenario_id=scenario.id,
                passed=False,
                score=0.0,
                output="",
                judge_feedback="",
                error=str(e),
                attempt=1,
            )

    tasks = [run_one(s) for s in scenarios]
    name_results = await asyncio.gather(*tasks)

    for idx, (name, result) in enumerate(name_results, 1):
        status = "PASS" if result.passed else "FAIL"
        click.echo(f"  [{idx}/{len(name_results)}] {name}... {status} ({result.score:.2f}/1.00)")
    results = [r for _, r in name_results]

    passed = sum(1 for r in results if r.passed)
    total_score = sum(r.score for r in results)

    run_duration = time.monotonic() - run_start

    # Write results to DB in a single transaction
    conn = _get_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        _upsert_scenarios(conn, course_name, scenarios)

        conn.execute(
            """INSERT INTO runs
               (id, model, skills, course, total_scenarios, passed_scenarios, total_score,
                duration_seconds, git_sha, judge_model)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                run_id,
                resolved_model,
                json.dumps(skills),
                course_name,
                len(scenarios),
                passed,
                total_score,
                run_duration,
                git_sha,
                judge.judge_model,
            ),
        )

        for r in results:
            conn.execute(
                """INSERT INTO scenario_results
                   (id, run_id, scenario_id, passed, score, output, judge_feedback,
                    duration_seconds, error, attempt)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    str(uuid.uuid4()),
                    run_id,
                    r.scenario_id,
                    1 if r.passed else 0,
                    r.score,
                    r.output,
                    r.judge_feedback,
                    None,
                    r.error,
                    r.attempt,
                ),
            )

        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()

    await harness.close()

    click.echo(
        f"\nRun complete: {passed}/{len(scenarios)} passed, "
        f"score: {total_score:.2f}/{sum(s.max_score for s in scenarios):.2f}, "
        f"duration: {run_duration:.1f}s"
    )
    click.echo(f"Run ID: {run_id}")

    return {
        "run_id": run_id,
        "passed": passed,
        "total": len(scenarios),
        "score": total_score,
        "duration": run_duration,
    }


# --- CLI ---


@click.group()
def cli() -> None:
    """benchmark eval — AI model evaluation framework."""


@cli.command()
@click.option("--course", required=True, help="Course name (subdirectory under courses/)")
@click.option("--model", default=None, help="Model identifier (default: $DOJO_MODEL)")
@click.option("--skills", default="", help="Comma-separated skill names")
@click.option("--judge-mode", default=None, help="Judge mode: simple|llm (default: $DOJO_JUDGE_MODE)")
@click.option("--judge-model", default=None, help="Judge model (default: $DOJO_JUDGE_MODEL)")
@click.option("--num-runs", default=1, type=int, help="Number of repeated runs (default: 1)")
def run(
    course: str,
    model: str | None,
    skills: str,
    judge_mode: str | None,
    judge_model: str | None,
    num_runs: int,
) -> None:
    """Run all scenarios in a course."""
    skills_list = [s.strip() for s in skills.split(",") if s.strip()]
    all_results: list[dict[str, Any]] = []
    for i in range(num_runs):
        if num_runs > 1:
            click.echo(f"\n--- Run {i+1}/{num_runs} ---")
        result = asyncio.run(
            _run_course(
                course_name=course,
                model=model or "",
                skills=skills_list,
                judge_mode=judge_mode,
                judge_model=judge_model,
            )
        )
        all_results.append(result)

    if num_runs > 1:
        scores = [r["score"] for r in all_results]
        passed_vals = [r["passed"] for r in all_results]
        avg_score = sum(scores) / len(scores)
        avg_passed = sum(passed_vals) / len(passed_vals)
        click.echo(f"\n{'='*50}")
        click.echo(f"Aggregated over {num_runs} runs:")
        click.echo(f"  Avg Passed: {avg_passed:.1f}/{all_results[0]['total']}")
        click.echo(f"  Avg Score:  {avg_score:.2f}")
        click.echo(f"  Min Score:  {min(scores):.2f}")
        click.echo(f"  Max Score:  {max(scores):.2f}")
        all_passed = all(r["passed"] == r["total"] for r in all_results)
        if not all_passed:
            raise SystemExit(1)


@cli.command(name="list-courses")
def list_courses() -> None:
    """List available courses."""
    if not _COURSES_DIR.exists():
        click.echo("No courses directory found.")
        return

    courses = sorted(d.name for d in _COURSES_DIR.iterdir() if d.is_dir())
    if not courses:
        click.echo("No courses found.")
        return

    click.echo("Available courses:")
    for name in courses:
        dojo_path = _COURSES_DIR / name / "dojo.md"
        alt_path = _COURSES_DIR / name / "dojo.yaml"
        status = "✓" if (dojo_path.exists() or alt_path.exists()) else "✗ (no dojo.md)"
        click.echo(f"  {status} {name}")


@cli.command(name="list-runs")
@click.option("--limit", default=20, help="Number of recent runs to show")
def list_runs(limit: int) -> None:
    """List recent evaluation runs."""
    import sqlite3

    _init_db()
    conn = _get_db()
    try:
        rows = conn.execute(
            """SELECT id, model, course, created_at, total_scenarios, passed_scenarios,
                      total_score, duration_seconds
               FROM runs ORDER BY created_at DESC LIMIT ?""",
            (limit,),
        ).fetchall()

        if not rows:
            click.echo("No runs found.")
            return

        click.echo(f"{'Run ID':<40} {'Model':<20} {'Course':<20} {'Passed':<8} {'Score':<8} {'Duration':<10}")
        click.echo("-" * 110)
        for row in rows:
            click.echo(
                f"{row['id']:<40} {row['model']:<20} {row['course']:<20} "
                f"{row['passed_scenarios']}/{row['total_scenarios']:<5} "
                f"{row['total_score']:<8.2f} "
                f"{row['duration_seconds'] or 0:<10.1f}s"
            )
    finally:
        conn.close()


@cli.command(name="show-run")
@click.option("--id", "run_id", required=True, help="Run ID to inspect")
def show_run(run_id: str) -> None:
    """Show details for a specific run."""
    import sqlite3

    _init_db()
    conn = _get_db()
    conn.row_factory = sqlite3.Row
    try:
        run = conn.execute(
            """SELECT * FROM runs WHERE id = ?""",
            (run_id,),
        ).fetchone()

        if run is None:
            raise click.ClickException(f"Run not found: {run_id}")

        click.echo(f"Run ID:       {run['id']}")
        click.echo(f"Model:        {run['model']}")
        click.echo(f"Course:       {run['course']}")
        click.echo(f"Skills:       {run['skills']}")
        click.echo(f"Date:         {run['created_at']}")
        click.echo(f"Judge Model:  {run['judge_model']}")
        click.echo(f"Git SHA:      {run['git_sha']}")
        click.echo(f"Passed:       {run['passed_scenarios']}/{run['total_scenarios']}")
        click.echo(f"Score:        {run['total_score']:.2f}")
        click.echo(f"Duration:     {run['duration_seconds']:.1f}s")
        click.echo("")

        results = conn.execute(
            """SELECT sr.*, s.name as scenario_name, s.difficulty, s.max_score
               FROM scenario_results sr
               JOIN scenarios s ON sr.scenario_id = s.id
               WHERE sr.run_id = ?
               ORDER BY sr.attempt, s.name""",
            (run_id,),
        ).fetchall()

        if not results:
            click.echo("No results found for this run.")
            return

        click.echo(f"{'Scenario':<40} {'Difficulty':<12} {'Passed':<8} {'Score':<8}")
        click.echo("-" * 70)
        for r in results:
            status = "PASS" if r["passed"] else "FAIL"
            click.echo(
                f"{r['scenario_name']:<40} {r['difficulty']:<12} "
                f"{status:<8} {r['score']:<8.2f}"
            )
            if r["error"]:
                click.echo(f"  Error: {r['error']}")

    finally:
        conn.close()


if __name__ == "__main__":
    cli()
