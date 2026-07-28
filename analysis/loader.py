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

TraceDict = Dict[str, Any]


def get_dataset_info(name: str) -> dict[str, Any]:
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
    import time as _time
    start = _time.time()
    dataset_name = config.resolve_dataset()

    try:
        ds = load_dataset(
            dataset_name,
            split="train",
            streaming=False,
            cache_dir=config.cache_dir,
        )
        elapsed_s = _time.time() - start
        import rich
        rich.print(f"[dim]Dataset loaded: {len(ds)} rows in {elapsed_s:.0f}s (non-streaming)[/]")
        return _iter_batches_nonstreaming(ds, config)
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

    return _iter_batches_streaming(ds, config)


def _try_fallback(
    config: AnalysisConfig,
) -> Iterator[Dataset | IterableDataset]:
    try:
        ds = load_dataset(
            FALLBACK_DATASET,
            split="train",
            streaming=True,
            cache_dir=config.cache_dir,
        )
        return _iter_batches_streaming(ds, config)
    except Exception as exc:
        raise RuntimeError(
            f"Primary and fallback datasets unavailable: {exc}"
        ) from exc


def _iter_batches_nonstreaming(
    ds: Dataset,
    config: AnalysisConfig,
) -> Generator[Dataset, None, None]:
    total = len(ds)
    n = min(total, config.max_samples) if config.max_samples > 0 else total
    for i in range(0, n, config.batch_size):
        end = min(i + config.batch_size, n)
        yield ds.select(range(i, end))


def _iter_batches_streaming(
    ds: IterableDataset,
    config: AnalysisConfig,
) -> Generator[Dataset, None, None]:
    from datasets import Dataset as BatchDataset
    batch: list[dict[str, Any]] = []
    count = 0

    for row in ds:
        batch.append(row)
        if len(batch) >= config.batch_size:
            yield BatchDataset.from_list(batch)
            batch.clear()
            count += config.batch_size

        if config.max_samples > 0 and count + len(batch) >= config.max_samples:
            break

    if batch:
        yield BatchDataset.from_list(batch)


def extract_trace(row: dict[str, Any], is_wrapper: bool) -> TraceDict | None:
    if is_wrapper:
        return _extract_wrapper(row)
    return _extract_raw(row)


def _extract_wrapper(row: dict[str, Any]) -> TraceDict | None:
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

    return _normalize_trace(parsed)


def _extract_raw(row: dict[str, Any]) -> TraceDict | None:
    return _normalize_trace(row)


def _normalize_trace(data: dict[str, Any]) -> TraceDict | None:
    aliases: dict[str, list[str]] = {
        "uid": ["uid", "id", "trace_id", "ID", "leafUuid", "leaf_uuid"],
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

    if "cot" not in result:
        result["cot"] = ""

    return result if result.get("uid") or result.get("cot") is not None else None


def iter_traces(
    config: AnalysisConfig | None = None,
) -> Generator[TraceDict, None, None]:
    cfg = config or AnalysisConfig()
    is_wrapper = cfg.is_wrapper_format
    count = 0

    for batch in load_dataset_simple(cfg):
        for row in batch:
            trace = extract_trace(row, is_wrapper)
            if trace is not None:
                yield trace
                count += 1

            if cfg.max_samples > 0 and count >= cfg.max_samples:
                return


def count_traces(config: AnalysisConfig | None = None) -> int:
    count = 0
    for _ in iter_traces(config):
        count += 1
    return count
