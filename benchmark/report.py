"""CLI for generating HTML reports and trend charts from evaluation results."""

import json
import sqlite3
from pathlib import Path
from typing import Any, Final

import click

from benchmark.eval import _get_db, _init_db

_RESULTS_DIR: Final = Path(__file__).resolve().parent / "results"

_CHART_JS_CDN: Final = "https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"

_TABLE_STYLE: Final = """
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
       margin: 2rem; background: #f8f9fa; color: #333; }
h1 { color: #1a1a2e; }
h2 { color: #16213e; margin-top: 2rem; }
.chart-container { max-width: 900px; margin: 2rem 0; background: white;
                   padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
table { width: 100%; border-collapse: collapse; margin: 1rem 0;
        background: white; border-radius: 8px; overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
th, td { padding: 0.75rem 1rem; text-align: left; }
th { background: #16213e; color: white; font-weight: 600; }
tr:nth-child(even) { background: #f1f3f5; }
.pass { color: #2b8a3e; font-weight: 600; }
.fail { color: #c92a2a; font-weight: 600; }
.summary-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                 gap: 1rem; margin: 1rem 0; }
.card { background: white; padding: 1.2rem; border-radius: 8px;
        text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.card-value { font-size: 2rem; font-weight: 700; color: #16213e; }
.card-label { font-size: 0.85rem; color: #868e96; margin-top: 0.3rem; }
"""


def _fetch_runs(course: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
    """Fetch runs from the database."""
    conn = _get_db()
    try:
        if course:
            rows = conn.execute(
                """SELECT id, model, course, created_at, total_scenarios, passed_scenarios,
                          total_score, duration_seconds, skills, git_sha, judge_model
                   FROM runs WHERE course = ? ORDER BY created_at DESC LIMIT ?""",
                (course, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT id, model, course, created_at, total_scenarios, passed_scenarios,
                          total_score, duration_seconds, skills, git_sha, judge_model
                   FROM runs ORDER BY created_at DESC LIMIT ?""",
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def _fetch_run_details(run_id: str) -> dict[str, Any] | None:
    """Fetch a single run with its scenario results."""
    conn = _get_db()
    conn.row_factory = sqlite3.Row
    try:
        run = conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
        if run is None:
            return None
        results = conn.execute(
            """SELECT sr.*, s.name as scenario_name, s.difficulty, s.max_score, s.tags
               FROM scenario_results sr
               JOIN scenarios s ON sr.scenario_id = s.id
               WHERE sr.run_id = ?
               ORDER BY s.name""",
            (run_id,),
        ).fetchall()
        return {"run": dict(run), "results": [dict(r) for r in results]}
    finally:
        conn.close()


def _render_dashboard_html(runs: list[dict[str, Any]]) -> str:
    """Generate a self-contained HTML dashboard with Chart.js."""
    runs_json = json.dumps(runs)
    now = __import__("datetime").datetime.now(__import__("datetime").UTC).strftime("%Y-%m-%d %H:%M UTC")

    latest = runs[0] if runs else {}
    total_runs = len(runs)
    avg_pass_rate = (
        sum(r["passed_scenarios"] / max(r["total_scenarios"], 1) for r in runs) / max(total_runs, 1) * 100
    )
    models = sorted({r["model"] for r in runs})
    courses = sorted({r["course"] for r in runs})

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Benchmark Dashboard</title>
<script src="{_CHART_JS_CDN}"></script>
<style>{_TABLE_STYLE}</style>
</head>
<body>
<h1>🧪 Benchmark Dashboard</h1>
<p>Generated: {now} | Runs: {total_runs} | Models: {', '.join(models) if models else 'N/A'}</p>

<div class="summary-cards">
  <div class="card">
    <div class="card-value">{latest.get('passed_scenarios', 0)}/{latest.get('total_scenarios', 0)}</div>
    <div class="card-label">Latest Run Passed</div>
  </div>
  <div class="card">
    <div class="card-value">{avg_pass_rate:.1f}%</div>
    <div class="card-label">Avg Pass Rate</div>
  </div>
  <div class="card">
    <div class="card-value">{latest.get('total_score', 0):.1f}</div>
    <div class="card-label">Latest Score</div>
  </div>
  <div class="card">
    <div class="card-value">{latest.get('duration_seconds', 0):.1f}s</div>
    <div class="card-label">Latest Duration</div>
  </div>
</div>

<div class="chart-container">
  <canvas id="scoreChart"></canvas>
</div>

<div class="chart-container">
  <canvas id="passChart"></canvas>
</div>

<h2>Latest Run Summary</h2>
<table>
  <tr><th>Field</th><th>Value</th></tr>
  <tr><td>Run ID</td><td>{latest.get('id', 'N/A')}</td></tr>
  <tr><td>Model</td><td>{latest.get('model', 'N/A')}</td></tr>
  <tr><td>Course</td><td>{latest.get('course', 'N/A')}</td></tr>
  <tr><td>Date</td><td>{latest.get('created_at', 'N/A')}</td></tr>
  <tr><td>Score</td><td>{latest.get('total_score', 0):.2f}</td></tr>
  <tr><td>Passed</td><td>{latest.get('passed_scenarios', 0)}/{latest.get('total_scenarios', 0)}</td></tr>
  <tr><td>Duration</td><td>{latest.get('duration_seconds', 0):.1f}s</td></tr>
  <tr><td>Judge</td><td>{latest.get('judge_model', 'N/A')}</td></tr>
</table>

<h2>All Runs</h2>
<table>
  <tr><th>Date</th><th>Model</th><th>Course</th><th>Passed</th><th>Score</th><th>Duration</th></tr>
  {''.join(f'<tr><td>{r["created_at"][:19]}</td><td>{r["model"]}</td><td>{r["course"]}</td>'
           f'<td class="{"pass" if r["passed_scenarios"] == r["total_scenarios"] else "fail"}">'
           f'{r["passed_scenarios"]}/{r["total_scenarios"]}</td>'
           f'<td>{r["total_score"]:.2f}</td>'
           f'<td>{r["duration_seconds"] or 0:.1f}s</td></tr>'
           for r in runs)}
</table>

<script>
const runs = {runs_json};
const labels = runs.map(r => (r.created_at || '').slice(0, 19)).reverse();
const models = [...new Set(runs.map(r => r.model))];

const modelColors = {{}};
const palette = ['#4e79a7','#f28e2b','#e15759','#76b7b2','#59a14f','#edc948','#b07aa1','#ff9da7'];
models.forEach((m, i) => {{ modelColors[m] = palette[i % palette.length]; }});

// Score chart
new Chart(document.getElementById('scoreChart'), {{
  type: 'line',
  data: {{
    labels: labels,
    datasets: models.map(model => ({{
      label: model,
      data: runs.filter(r => r.model === model).map(r => r.total_score).reverse(),
      borderColor: modelColors[model],
      backgroundColor: modelColors[model] + '33',
      tension: 0.3,
      fill: false,
      spanGaps: true,
    }}))
  }},
  options: {{
    responsive: true,
    plugins: {{ title: {{ display: true, text: 'Score Over Time' }} }},
    scales: {{ y: {{ beginAtZero: true }} }}
  }}
}});

// Pass rate chart
new Chart(document.getElementById('passChart'), {{
  type: 'bar',
  data: {{
    labels: labels,
    datasets: models.map(model => ({{
      label: model,
      data: runs.filter(r => r.model === model).map(r =>
        r.total_scenarios > 0 ? (r.passed_scenarios / r.total_scenarios * 100) : 0
      ).reverse(),
      backgroundColor: models.map(m => modelColors[m]),
    }}))
  }},
  options: {{
    responsive: true,
    plugins: {{ title: {{ display: true, text: 'Pass Rate Over Time (%)' }} }},
    scales: {{ y: {{ beginAtZero: true, max: 100 }} }}
  }}
}});
</script>
</body>
</html>"""


def _render_trend_html(runs: list[dict[str, Any]], course: str) -> str:
    """Generate a trend chart HTML for a specific course."""
    runs_json = json.dumps(runs)
    now = __import__("datetime").datetime.now(__import__("datetime").UTC).strftime("%Y-%m-%d %H:%M UTC")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Trend: {course}</title>
<script src="{_CHART_JS_CDN}"></script>
<style>{_TABLE_STYLE}</style>
</head>
<body>
<h1>📈 Trend: {course}</h1>
<p>Generated: {now} | {len(runs)} runs</p>

<div class="chart-container">
  <canvas id="trendChart"></canvas>
</div>

<table>
  <tr><th>Date</th><th>Model</th><th>Passed</th><th>Score</th><th>Duration</th></tr>
  {''.join(f'<tr><td>{r["created_at"][:19]}</td><td>{r["model"]}</td>'
           f'<td class="{"pass" if r["passed_scenarios"] == r["total_scenarios"] else "fail"}">'
           f'{r["passed_scenarios"]}/{r["total_scenarios"]}</td>'
           f'<td>{r["total_score"]:.2f}</td>'
           f'<td>{r["duration_seconds"] or 0:.1f}s</td></tr>'
           for r in runs)}
</table>

<script>
const runs = {runs_json};
const labels = runs.map(r => (r.created_at || '').slice(0, 19)).reverse();
const models = [...new Set(runs.map(r => r.model))];

const palette = ['#4e79a7','#f28e2b','#e15759','#76b7b2','#59a14f','#edc948','#b07aa1','#ff9da7'];

new Chart(document.getElementById('trendChart'), {{
  type: 'line',
  data: {{
    labels: labels,
    datasets: models.map((model, i) => ({{
      label: model,
      data: runs.filter(r => r.model === model).map(r => r.total_score).reverse(),
      borderColor: palette[i % palette.length],
      tension: 0.3,
      fill: false,
      spanGaps: true,
    }}))
  }},
  options: {{
    responsive: true,
    plugins: {{ title: {{ display: true, text: 'Score Trend for ' + '{course}' }} }},
    scales: {{ y: {{ beginAtZero: true }} }}
  }}
}});
</script>
</body>
</html>"""


def _render_comparison_html(run_a: dict[str, Any], run_b: dict[str, Any]) -> str:
    """Generate a side-by-side comparison of two runs."""
    details_a = run_a["results"]
    details_b = run_b["results"]
    run_a_data = run_a["run"]
    run_b_data = run_b["run"]

    scenarios_a = {r["scenario_name"]: r for r in details_a}
    scenarios_b = {r["scenario_name"]: r for r in details_b}
    all_scenarios = sorted(set(scenarios_a) | set(scenarios_b))

    now = __import__("datetime").datetime.now(__import__("datetime").UTC).strftime("%Y-%m-%d %H:%M UTC")

    rows_html = ""
    for name in all_scenarios:
        a = scenarios_a.get(name)
        b = scenarios_b.get(name)

        if a:
            a_cls = "pass" if a["passed"] else "fail"
            a_lbl = "PASS" if a["passed"] else "FAIL"
            a_status = f'<span class="{a_cls}">{a_lbl}</span>'
            a_score = f"{a['score']:.2f}"
        else:
            a_status = "\u2014"
            a_score = "\u2014"

        if b:
            b_cls = "pass" if b["passed"] else "fail"
            b_lbl = "PASS" if b["passed"] else "FAIL"
            b_status = f'<span class="{b_cls}">{b_lbl}</span>'
            b_score = f"{b['score']:.2f}"
        else:
            b_status = "\u2014"
            b_score = "\u2014"

        diff = ""
        if a and b:
            d = b["score"] - a["score"]
            if d > 0:
                diff_color = "#2b8a3e"
            elif d < 0:
                diff_color = "#c92a2a"
            else:
                diff_color = "#868e96"
            diff = f'<span style="color:{diff_color}">{d:+.2f}</span>'

        rows_html += f"<tr><td>{name}</td><td>{a_status} {a_score}</td><td>{b_status} {b_score}</td><td>{diff}</td></tr>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Run Comparison</title>
<style>{_TABLE_STYLE}</style>
</head>
<body>
<h1>⚖️ Run Comparison</h1>
<p>Generated: {now}</p>

<table>
  <tr><th></th><th>Run A</th><th>Run B</th></tr>
  <tr><td><strong>ID</strong></td><td>{run_a_data["id"]}</td><td>{run_b_data["id"]}</td></tr>
  <tr><td><strong>Model</strong></td><td>{run_a_data["model"]}</td><td>{run_b_data["model"]}</td></tr>
  <tr><td><strong>Course</strong></td><td>{run_a_data["course"]}</td><td>{run_b_data["course"]}</td></tr>
  <tr><td><strong>Date</strong></td><td>{run_a_data["created_at"]}</td><td>{run_b_data["created_at"]}</td></tr>
  <tr><td><strong>Passed</strong></td><td>{run_a_data["passed_scenarios"]}/{run_a_data["total_scenarios"]}</td>
      <td>{run_b_data["passed_scenarios"]}/{run_b_data["total_scenarios"]}</td></tr>
  <tr><td><strong>Score</strong></td><td>{run_a_data["total_score"]:.2f}</td><td>{run_b_data["total_score"]:.2f}</td></tr>
  <tr><td><strong>Duration</strong></td><td>{run_a_data["duration_seconds"] or 0:.1f}s</td>
      <td>{run_b_data["duration_seconds"] or 0:.1f}s</td></tr>
</table>

<h2>Per-Scenario Comparison</h2>
<table>
  <tr><th>Scenario</th><th>Run A</th><th>Run B</th><th>Diff</th></tr>
  {rows_html}
</table>
</body>
</html>"""


# --- CLI ---


@click.group()
def cli() -> None:
    """benchmark report — generate HTML reports and charts."""


@cli.command()
@click.option("--course", default=None, help="Filter by course name")
@click.option("--output", default=None, help="Output HTML file path")
@click.option("--open/--no-open", default=False, help="Open in browser after generation")
def dashboard(
    course: str | None,
    output: str | None,
    open: bool,
) -> None:
    """Generate a full dashboard HTML with Chart.js trends."""
    _init_db()
    runs = _fetch_runs(course=course, limit=100)
    if not runs:
        click.echo("No runs found. Run an evaluation first.")
        return

    html = _render_dashboard_html(runs)
    path = _write_html(html, output, f"dashboard-{course or 'all'}.html")
    click.echo(f"Dashboard written to {path}")

    if open:
        _open_in_browser(path)


@cli.command()
@click.option("--course", required=True, help="Course name")
@click.option("--output", default=None, help="Output HTML file path")
@click.option("--open/--no-open", default=False, help="Open in browser")
def trend(
    course: str,
    output: str | None,
    open: bool,
) -> None:
    """Generate a trend chart for a specific course."""
    _init_db()
    runs = _fetch_runs(course=course, limit=100)
    if not runs:
        click.echo(f"No runs found for course '{course}'.")
        return

    html = _render_trend_html(runs, course)
    path = _write_html(html, output, f"trend-{course}.html")
    click.echo(f"Trend chart written to {path}")

    if open:
        _open_in_browser(path)


@cli.command()
@click.option("--run-a", required=True, help="First run ID")
@click.option("--run-b", required=True, help="Second run ID")
@click.option("--output", default=None, help="Output HTML file path")
@click.option("--open/--no-open", default=False, help="Open in browser")
def compare(
    run_a: str,
    run_b: str,
    output: str | None,
    open: bool,
) -> None:
    """Compare two runs side-by-side."""
    _init_db()
    details_a = _fetch_run_details(run_a)
    if details_a is None:
        raise click.ClickException(f"Run not found: {run_a}")
    details_b = _fetch_run_details(run_b)
    if details_b is None:
        raise click.ClickException(f"Run not found: {run_b}")

    html = _render_comparison_html(details_a, details_b)
    path = _write_html(html, output, f"compare-{run_a[:8]}-{run_b[:8]}.html")
    click.echo(f"Comparison written to {path}")

    if open:
        _open_in_browser(path)


def _write_html(html: str, output_path: str | None, default_name: str) -> Path:
    """Write HTML to file, returning the path."""
    if output_path:
        path = Path(output_path)
    else:
        _RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        path = _RESULTS_DIR / default_name
    path.write_text(html)
    return path


def _open_in_browser(path: Path) -> None:
    """Open the HTML file in the default browser."""
    import webbrowser

    webbrowser.open(f"file://{path.resolve()}")


if __name__ == "__main__":
    cli()
