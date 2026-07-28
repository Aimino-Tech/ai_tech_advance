"""Dataset loader for Fable 5 traces from HuggingFace.

Handles both wrapper format (Crownelius, data in row_json)
and raw format (Glint-Research, fields as direct columns).
"""

import json
from collections.abc import Generator, Iterator
from typing import Any, Dict, List, Optional

from datasets import Dataset, IterableDataset, load_dataset, load_dataset_builder

from analysis.config import (
    FALLBACK_DATASET,
    TRACE_FIELDS,
    AnalysisConfig,
)

# ── Trace type ───────────────────────────────────────────────────

TraceDict = Dict[str, Any]
"""A single parsed trace with fields: uid, source_file, session, model,
context, cot, output_type, output, completion, origin."""

# ── Dataset loading ──────────────────────────────────────────────


def get_dataset_info(name: str) -> dict[str, Any]:
    """Check if a dataset exists and return its metadata.

    Raises RuntimeError if the dataset is not accessible.
    """
    try:
        builder = load_dataset_builder(name)
        return {
            "name": name,
            "configs": builder.configs,
            "description": builder.info.description if builder.info else "",
            "features": str(builder.info.features) if builder.info else "",
            "splits": str(builder.info.splits) if builder.info else "",
        }
    except Exception as exc:
        raise RuntimeError(f"Cannot access dataset '{name}': {exc}") from exc


def load_dataset_simple(
    config: AnalysisConfig,
) -> Iterator[Dataset | IterableDataset]:
    """Load dataset from HuggingFace with streaming.

    Returns an iterator over batched Dataset slices (each of size
    config.batch_size). Uses streaming to avoid loading the full
    2M-row dataset into memory.
    """
    import time
    start = time.time()
    dataset_name = config.resolve_dataset()

    try:
        ds = load_dataset(
            dataset_name,
            split="train",
            streaming=False,
            cache_dir=config.cache_dir,
        )
        elapsed_s = time.time() - start
        if isinstance(ds, Dataset):
            import rich
            rich.print(f"[dim]Dataset loaded: {len(ds)} rows in {elapsed_s:.0f}s (non-streaming)[/]")
            return _iter_batches(ds, config)
    except Exception:
        pass

    try:
        ds = load_dataset(
            dataset_name,
            split="train",
            streaming=True,
            cache_dir=config.cache_dir,
        )
    except Exception as exc:
        if config.fallback and dataset_name != FALLBACK_DATASET:
            return _try_fallback(config)
        raise RuntimeError(
            f"Failed to load dataset '{dataset_name}': {exc}"
        ) from exc

    return _iter_batches(ds, config)


def _try_fallback(
    config: AnalysisConfig,
) -> Iterator[Dataset | IterableDataset]:
    """Attempt to load from the fallback dataset."""
    try:
        ds = load_dataset(
            FALLBACK_DATASET,
            split="train",
            streaming=True,
            cache_dir=config.cache_dir,
        )
        return _iter_batches(ds, config)
    except Exception as exc:
        raise RuntimeError(
            f"Primary and fallback datasets unavailable: {exc}"
        ) from exc


def _iter_batches(
    ds: IterableDataset,
    config: AnalysisConfig,
) -> Generator[Dataset, None, None]:
    """Yield rows from iterable dataset in batches of batch_size."""
    batch: list[dict[str, Any]] = []
    count = 0

    for row in ds:
        batch.append(row)  # type: ignore[arg-type]
        if len(batch) >= config.batch_size:
            # Build a temporary Dataset slice
            from datasets import Dataset as BatchDataset  # noqa: PLC0415

            yield BatchDataset.from_list(batch)  # type: ignore[no-untyped-call]
            batch.clear()
            count += config.batch_size

        if config.max_samples > 0 and count + len(batch) >= config.max_samples:
            break

    if batch:
        from datasets import Dataset as BatchDataset  # noqa: PLC0415

        yield BatchDataset.from_list(batch)  # type: ignore[no-untyped-call]


# ── Trace extraction ─────────────────────────────────────────────


def extract_trace(row: dict[str, Any], is_wrapper: bool) -> TraceDict | None:
    """Extract a parsed trace dict from a single row.

    Handles both wrapper format (Crownelius) where trace data is
    a JSON string in the ``row_json`` column, and raw format
    (Glint-Research) where fields are direct columns.

    Returns None if the row cannot be parsed (malformed JSON, missing
    required fields).
    """
    if is_wrapper:
        return _extract_wrapper(row)
    return _extract_raw(row)


def _extract_wrapper(row: dict[str, Any]) -> TraceDict | None:
    """Parse a wrapper-format row (Crownelius)."""
    raw_json = row.get("row_json")
    if not raw_json:
        return None

    if isinstance(raw_json, str):
        try:
            parsed: dict[str, Any] = json.loads(raw_json)
        except (json.JSONDecodeError, TypeError):
            return None
    elif isinstance(raw_json, dict):
        parsed = raw_json
    else:
        return None

    # Normalize field names — row_json may use different casing
    return _normalize_trace(parsed)


def _extract_raw(row: dict[str, Any]) -> TraceDict | None:
    """Parse a raw-format row (Glint-Research)."""
    return _normalize_trace(row)


def _normalize_trace(data: dict[str, Any]) -> TraceDict | None:
    """Map various field name conventions to canonical names.

    The row_json field may have keys like 'cot', 'CoT', 'chain_of_thought',
    'context', 'Context', 'instruction', etc.
    """
    aliases: dict[str, list[str]] = {
        "uid": ["uid", "id", "trace_id", "ID"],
        "source_file": ["source_file", "source", "file"],
        "session": ["session", "session_id", "Session"],
        "model": ["model", "Model", "model_name", "model_id"],
        "context": [
            "context",
            "Context",
            "instruction",
            "user_input",
            "prompt",
            "messages",
        ],
        "cot": [
            "cot",
            "CoT",
            "chain_of_thought",
            "reasoning",
            "reasoning_trace",
            "thought",
            "scratchpad",
        ],
        "output_type": [
            "output_type",
            "output_type",
            "type",
            "response_type",
        ],
        "output": [
            "output",
            "response",
            "answer",
            "tool_call",
            "tool_calls",
            "completion",
        ],
        "completion": [
            "completion",
            "full_output",
            "full_response",
            "raw_output",
        ],
        "origin": [
            "origin",
            "dataset",
            "source",
            "Origin",
        ],
    }

    result: TraceDict = {}
    for canonical, candidates in aliases.items():
        for key in candidates:
            if key in data and data[key] is not None:
                result[canonical] = data[key]
                break

    if not result.get("uid"):
        return None

    # Ensure cot exists (even if empty)
    if "cot" not in result:
        result["cot"] = ""

    return result


# ── Generator API ────────────────────────────────────────────────


def iter_traces(
    config: AnalysisConfig | None = None,
) -> Generator[TraceDict, None, None]:
    """Generator that yields parsed trace dicts one at a time.

    Handles both wrapper and raw formats automatically based on the
    dataset configured. Uses streaming to avoid loading the full
    dataset into memory.

    Usage::

        for trace in iter_traces():
            print(trace["cot"][:100])
    """
    cfg = config or AnalysisConfig()
    is_wrapper = cfg.is_wrapper_format
    count = 0

    for batch in load_dataset_simple(cfg):
        for row in batch:  # type: ignore[union-attr]
            trace = extract_trace(row, is_wrapper)  # type: ignore[arg-type]
            if trace is not None:
                yield trace
                count += 1

            if cfg.max_samples > 0 and count >= cfg.max_samples:
                return


def count_traces(config: AnalysisConfig | None = None) -> int:
    """Count available traces in the dataset (up to max_samples).

    Runs as a lightweight pass without storing results.
    """
    count = 0
    for _ in iter_traces(config):
        count += 1
    return count
