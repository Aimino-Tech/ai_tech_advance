#!/usr/bin/env python3
"""Fable 5 Pattern Extraction Pipeline — Main Orchestrator.

Loads Fable 5 traces from HuggingFace, classifies by skill,
extracts CoT / tool / behavioral patterns per skill, and writes
YAML pattern files and a combined stats JSON.

Usage:
    python -m analysis.run_analysis [--max-samples N] [--output-dir ...]
    python -m analysis.run_analysis --dry-run --max-samples 5
    python -m analysis.run_analysis --help
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

from analysis.classify_skills import (
    SKILL_CATEGORIES,
    SkillClassification,
    aggregate_skill_stats,
    classify_trace_skill,
)
from analysis.config import AnalysisConfig
from analysis.extract_behaviors import BehaviorStats, analyze_behaviors
from analysis.extract_cot import CotStats, analyze_cot_structure
from analysis.extract_tools import ToolUsageStats, analyze_tool_usage
from analysis.loader import iter_traces

console = Console()


# ── Pattern file schema helpers ──────────────────────────────────


def _cot_to_pattern_dict(stats: CotStats) -> dict[str, Any]:
    """Convert CotStats to a dict suitable for YAML output."""
    return {
        "total_traces": stats.total_traces,
        "cot_present": stats.cot_present,
        "cot_rate": stats.cot_rate,
        "avg_tokens": stats.avg_words,
        "avg_paragraphs": stats.avg_paragraphs,
        "avg_sentences": stats.avg_sentences,
        "avg_chars": stats.avg_chars,
        "median_tokens": stats.median_words,
        "max_tokens": stats.max_words,
        "min_tokens": stats.min_words,
        "opener_words": stats.opener_word_freq,
        "pronoun_first_pct": stats.pronoun_first_pct,
        "pronoun_second_pct": stats.pronoun_second_pct,
        "pronoun_third_pct": stats.pronoun_third_pct,
        "self_correction_rate": stats.self_correction_rate,
        "avg_self_corrections": stats.avg_self_corrections,
        "reasoning_connectors_per_turn": stats.avg_reasoning_connectors,
        "top_connectors": stats.top_connectors,
    }


def _tools_to_pattern_dict(stats: ToolUsageStats) -> dict[str, Any]:
    """Convert ToolUsageStats to a dict suitable for YAML output."""
    return {
        "total_traces": stats.total_traces,
        "traces_with_tools": stats.traces_with_tools,
        "tool_calls_per_trace": stats.tool_calls_per_trace,
        "tool_type_frequency": stats.tool_type_freq,
        "top_tool_calls": stats.top_tool_calls,
        "transition_matrix": stats.transition_matrix,
        "read_before_edit_rate": stats.read_before_edit_rate,
        "verify_after_action_rate": stats.verify_after_action_rate,
        "tool_to_text_ratio": stats.tool_to_text_ratio,
        "avg_tool_calls": stats.avg_tool_calls,
        "max_tool_calls": stats.max_tool_calls,
    }


def _behaviors_to_pattern_dict(stats: BehaviorStats) -> dict[str, Any]:
    """Convert BehaviorStats to a dict suitable for YAML output."""
    return {
        "total_traces": stats.total_traces,
        "self_correction_rate": stats.self_correction_rate,
        "avg_self_corrections": stats.avg_self_corrections,
        "hypothesis_driven_rate": stats.hypothesis_driven_rate,
        "avg_hypotheses": stats.avg_hypotheses,
        "multi_investigation_rate": stats.multi_investigation_rate,
        "step_coverage": stats.step_coverage,
        "step_transition_matrix": stats.step_transition_matrix,
        "same_turn_fix_rate": stats.same_turn_fix_rate,
    }


# ── YAML generation ──────────────────────────────────────────────


def generate_pattern_yaml(
    skill: str,
    trace_count: int,
    cot_stats: CotStats,
    tool_stats: ToolUsageStats,
    behavior_stats: BehaviorStats,
) -> dict[str, Any]:
    """Generate the YAML-compatible dict for a single skill category.

    The output structure mirrors the pattern files expected by
    downstream skills: stats, patterns, anti-patterns, steps.
    """
    cot_data = _cot_to_pattern_dict(cot_stats)
    tool_data = _tools_to_pattern_dict(tool_stats)
    behavior_data = _behaviors_to_pattern_dict(behavior_stats)

    # Derive patterns and anti-patterns from the data
    patterns: list[dict[str, Any]] = []
    anti_patterns: list[dict[str, Any]] = []

    # Pattern: self-correction
    sc_rate = behavior_data.get("self_correction_rate", 0)
    if sc_rate > 0.3:
        patterns.append({
            "name": "self-correction",
            "description": "Frequently corrects reasoning mid-turn",
            "frequency": sc_rate,
        })

    # Pattern: hypothesis-driven
    h_rate = behavior_data.get("hypothesis_driven_rate", 0)
    if h_rate > 0.3:
        patterns.append({
            "name": "hypothesis-driven-debugging",
            "description": "Forms and tests hypotheses before fixing",
            "frequency": h_rate,
        })

    # Pattern: read-before-edit
    rbe_rate = tool_data.get("read_before_edit_rate", 0)
    if rbe_rate > 0.2:
        patterns.append({
            "name": "read-before-edit",
            "description": "Reads/verifies current state before modifying",
            "frequency": rbe_rate,
        })

    # Pattern: verify-after-action
    vaa_rate = tool_data.get("verify_after_action_rate", 0)
    if vaa_rate > 0.2:
        patterns.append({
            "name": "verify-after-action",
            "description": "Follows actions with verification steps",
            "frequency": vaa_rate,
        })

    # Pattern: acknowledge-then-execute
    step_cov = behavior_data.get("step_coverage", {})
    ack_rate = step_cov.get("ACKNOWLEDGE", 0)
    exec_rate = step_cov.get("EXECUTE", 0)
    if ack_rate > 0.3:
        patterns.append({
            "name": "acknowledge-then-execute",
            "description": "Always acknowledges context before acting",
            "frequency": ack_rate,
        })

    # Anti-pattern: acting-without-scope
    scope_rate = step_cov.get("SCOPE", 0)
    if ack_rate > 0.5 and scope_rate < 0.2:
        anti_patterns.append({
            "name": "acting-without-scope",
            "description": "Proceeding without confirming requirements",
            "frequency": round(1.0 - scope_rate, 4),
        })

    # Anti-pattern: no-verification
    verify_rate = step_cov.get("VERIFY", 0)
    if verify_rate < 0.2:
        anti_patterns.append({
            "name": "no-verification",
            "description": "Completes work without verification step",
            "frequency": round(1.0 - verify_rate, 4),
        })

    # Steps with frequencies
    steps: list[dict[str, Any]] = []
    from analysis.extract_behaviors import STEPS  # noqa: PLC0415

    for step_name in STEPS:
        steps.append({
            "name": step_name,
            "frequency": step_cov.get(step_name, 0.0),
        })

    # Opener words list for patterns
    top_openers = list(cot_data.get("opener_words", {}).keys())[:5]
    if top_openers:
        patterns.insert(0, {
            "name": "common-openers",
            "description": f"Frequent utterance starters: {', '.join(top_openers)}",
            "frequency": cot_data.get("cot_rate", 0),
        })

    # Connectors
    top_conns = cot_data.get("top_connectors", [])
    if top_conns:
        patterns.append({
            "name": "reasoning-chaining",
            "description": f"Uses connectors like {', '.join(top_conns[:3])}",
            "frequency": round(min(cot_data.get("reasoning_connectors_per_turn", 0) / 5, 1.0), 4),
        })

    return {
        "skill": skill,
        "total_traces": trace_count,
        "stats": {
            "cot": cot_data,
            "tool_usage": tool_data,
            "behaviors": behavior_data,
        },
        "patterns": patterns,
        "anti_patterns": anti_patterns,
        "steps": steps,
    }


def write_pattern_yaml(
    skill: str,
    data: dict[str, Any],
    output_dir: Path,
) -> Path:
    """Write a single YAML pattern file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{skill}_patterns.yaml"
    with open(path, "w") as f:
        yaml.dump(
            data,
            f,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
            indent=2,
        )
    return path


# ── Main analysis ────────────────────────────────────────────────


def run_analysis(config: AnalysisConfig) -> dict[str, Any]:
    """Run the full analysis pipeline.

    Steps:
    1. Load dataset (streaming)
    2. Classify traces by skill (with progress bar)
    3. Per-skill: CoT analysis, tool analysis, behavioral analysis
    4. Generate YAML pattern files
    5. Generate combined stats JSON
    6. Print summary

    Returns a dict of results.
    """
    console.rule("[bold cyan]Fable 5 Pattern Extraction Pipeline[/]")
    console.print(f"Dataset: [yellow]{config.dataset_name}[/]")
    if config.max_samples > 0:
        console.print(f"Samples: [yellow]{config.max_samples}[/]")
    console.print(f"Output:  [yellow]{config.output_dir.resolve()}[/]")
    console.print()

    # ── Step 1: Load traces ──
    console.print("[bold]Step 1: Loading traces...[/]")
    traces: list[TraceDict] = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(
            "Loading traces...",
            total=config.max_samples if config.max_samples > 0 else None,
        )
        for trace in iter_traces(config):
            traces.append(trace)
            if progress.tasks:
                progress.update(task, advance=1)

    console.print(f"   Loaded [green]{len(traces)}[/] traces.")
    console.print()

    if not traces:
        console.print("[red]No traces loaded. Aborting.[/]")
        return {"error": "no_traces"}

    # ── Step 2: Classify by skill ──
    console.print("[bold]Step 2: Classifying traces by skill...[/]")
    classifications: list[SkillClassification] = []
    for trace in traces:
        cls = classify_trace_skill(trace)
        classifications.append(cls)

    skill_stats = aggregate_skill_stats(classifications)
    console.print(
        f"   Distribution: {dict(skill_stats.distribution_counts)}"
    )
    console.print()

    # ── Step 3: Per-skill analysis ──
    console.print("[bold]Step 3: Running per-skill analysis...[/]")

    # Group traces by skill
    skill_traces: dict[str, list[TraceDict]] = {s: [] for s in SKILL_CATEGORIES}
    for trace, cls in zip(traces, classifications):
        skill_traces[cls.skill].append(trace)

    # Run analysis per skill
    per_skill_data: dict[str, dict[str, Any]] = {}
    for skill in SKILL_CATEGORIES:
        skill_traces_list = skill_traces.get(skill, [])
        if not skill_traces_list:
            per_skill_data[skill] = _empty_skill_data()
            continue

        console.print(f"   Analyzing [cyan]{skill}[/] ({len(skill_traces_list)} traces)...")

        cot_stats = analyze_cot_structure(skill_traces_list)
        tool_stats = analyze_tool_usage(skill_traces_list)
        behavior_stats = analyze_behaviors(skill_traces_list)

        pattern_data = generate_pattern_yaml(
            skill=skill,
            trace_count=len(skill_traces_list),
            cot_stats=cot_stats,
            tool_stats=tool_stats,
            behavior_stats=behavior_stats,
        )
        per_skill_data[skill] = pattern_data

    if config.dry_run:
        console.print("[yellow]Dry run — skipping file output.[/]")
    else:
        # ── Step 4: Write YAML files ──
        console.print("[bold]Step 4: Writing YAML pattern files...[/]")
        output_dir = config.patterns_output_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        yaml_files: list[Path] = []
        for skill in SKILL_CATEGORIES:
            data = per_skill_data[skill]
            if data.get("total_traces", 0) == 0 and not config.dry_run:
                # Write minimal YAML even for empty skill
                data = _empty_skill_data(skill)
            path = write_pattern_yaml(skill, data, output_dir)
            yaml_files.append(path)
            console.print(f"   Written: [green]{path.name}[/]")

        # ── Step 5: Combined stats JSON ──
        console.print("[bold]Step 5: Writing combined stats JSON...[/]")
        combined: dict[str, Any] = {
            "pipeline_version": "0.1.0",
            "dataset": config.dataset_name,
            "total_traces": len(traces),
            "max_samples": config.max_samples,
            "skill_distribution": {
                skill: {
                    "count": skill_stats.distribution_counts.get(skill, 0),
                    "fraction": skill_stats.distribution.get(skill, 0.0),
                    "avg_confidence": skill_stats.avg_confidence.get(skill, 0.0),
                }
                for skill in SKILL_CATEGORIES
            },
            "per_skill": {
                skill: _build_combined_summary(per_skill_data.get(skill, {}))
                for skill in SKILL_CATEGORIES
            },
        }

        stats_path = config.stats_output_path
        with open(stats_path, "w") as f:
            json.dump(combined, f, indent=2, ensure_ascii=False)
        console.print(f"   Written: [green]{stats_path.name}[/]")

    # ── Summary ──
    console.print()
    console.rule("[bold cyan]Summary[/]")
    summary_table = Table(show_header=True, header_style="bold")
    summary_table.add_column("Skill", style="cyan")
    summary_table.add_column("Traces", justify="right")
    summary_table.add_column("Fraction", justify="right")
    summary_table.add_column("Avg Confidence", justify="right")
    summary_table.add_column("CoT Rate", justify="right")
    summary_table.add_column("Self-Correct", justify="right")

    for skill in SKILL_CATEGORIES:
        pd = per_skill_data.get(skill, {})
        stats = pd.get("stats", {})
        cot = stats.get("cot", {})
        behaviors = stats.get("behaviors", {})

        summary_table.add_row(
            skill,
            str(skill_stats.distribution_counts.get(skill, 0)),
            f"{skill_stats.distribution.get(skill, 0):.1%}",
            f"{skill_stats.avg_confidence.get(skill, 0):.1%}",
            f"{cot.get('cot_rate', 0):.1%}",
            f"{behaviors.get('self_correction_rate', 0):.1%}",
        )

    console.print(summary_table)

    total_files = len(SKILL_CATEGORIES) + 1  # YAMLs + JSON
    console.print(f"\n[bold green]Done![/] {len(traces)} traces analyzed.")
    if not config.dry_run:
        console.print(f"Generated {total_files} files in [yellow]{config.output_dir.resolve()}[/]")

    return {
        "total_traces": len(traces),
        "skill_stats": {
            "distribution": skill_stats.distribution,
            "avg_confidence": skill_stats.avg_confidence,
        },
        "per_skill": per_skill_data,
    }


def _empty_skill_data(skill: str = "unknown") -> dict[str, Any]:
    """Return an empty skill data structure."""
    return {
        "skill": skill,
        "total_traces": 0,
        "stats": {
            "cot": {},
            "tool_usage": {},
            "behaviors": {},
        },
        "patterns": [],
        "anti_patterns": [],
        "steps": [],
    }


def _build_combined_summary(per_skill: dict[str, Any]) -> dict[str, Any]:
    """Build a condensed summary from per-skill analysis data."""
    stats = per_skill.get("stats", {})
    cot = stats.get("cot", {})
    tool = stats.get("tool_usage", {})
    behavior = stats.get("behaviors", {})

    return {
        "trace_count": per_skill.get("total_traces", 0),
        "cot_rate": cot.get("cot_rate", 0),
        "avg_tokens": cot.get("avg_tokens", 0),
        "self_correction_rate": behavior.get("self_correction_rate", 0),
        "avg_tool_calls": tool.get("avg_tool_calls", 0),
        "read_before_edit_rate": tool.get("read_before_edit_rate", 0),
        "verify_after_action_rate": tool.get("verify_after_action_rate", 0),
    }


# ── CLI ──────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="Fable 5 Pattern Extraction Pipeline. "
        "Loads traces from HuggingFace and extracts behavioral patterns.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=0,
        help="Maximum traces to process (0 = all available)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="analysis/patterns",
        help="Output directory for YAML pattern files",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="",
        help="HuggingFace dataset name (default from config.py)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Rows per streaming batch",
    )
    parser.add_argument(
        "--fallback",
        action="store_true",
        help="Use fallback dataset if primary is unavailable",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Load samples but skip expensive analysis and file output",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for sampling",
    )
    return parser


def cli_entry() -> None:
    """Entry point for `python -m analysis.run_analysis`."""
    parser = build_parser()
    args = parser.parse_args()

    config = AnalysisConfig(
        max_samples=args.max_samples,
        batch_size=args.batch_size,
        fallback=args.fallback,
        dry_run=args.dry_run,
        seed=args.seed,
        output_dir=Path(args.output_dir),
    )
    if args.dataset:
        config = AnalysisConfig(
            max_samples=config.max_samples,
            batch_size=config.batch_size,
            fallback=config.fallback,
            dry_run=config.dry_run,
            seed=config.seed,
            output_dir=config.output_dir,
            dataset_name=args.dataset,
        )

    start = time.time()
    run_analysis(config)
    elapsed = time.time() - start
    console.print(f"\nElapsed: [yellow]{elapsed:.1f}s[/]")


if __name__ == "__main__":
    cli_entry()
