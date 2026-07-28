"""Configuration for the analysis pipeline."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Final

# ── HuggingFace Dataset Configuration ────────────────────────────

PRIMARY_DATASET: Final[str] = "Crownelius/Complete-FABLE.5-traces-2M"
FALLBACK_DATASET: Final[str] = "Glint-Research/Fable-5-traces"

# The wrapper format uses row_json; the raw format has fields directly.
# Crownelius = wrapper format, Glint-Research = raw format.
WRAPPER_DATASETS: Final[frozenset[str]] = frozenset({
    "Crownelius/Complete-FABLE.5-traces-2M",
})

# Column mapping for wrapper format
WRAPPER_COLUMNS: Final[list[str]] = [
    "row_hash",
    "first_source_dataset",
    "first_source_config",
    "first_source_split",
    "first_source_row_index",
    "seen_count",
    "row_json",
]

# Fields expected inside row_json
TRACE_FIELDS: Final[list[str]] = [
    "uid",
    "source_file",
    "session",
    "model",
    "context",
    "cot",
    "output_type",
    "output",
    "completion",
    "origin",
]


@dataclass(frozen=True, slots=True)
class AnalysisConfig:
    """Configuration for a single analysis run."""

    dataset_name: str = PRIMARY_DATASET
    """HuggingFace dataset identifier."""

    max_samples: int = 0
    """Max traces to process. 0 = all available (up to dataset size)."""

    batch_size: int = 1000
    """Number of rows to load per streaming batch."""

    cache_dir: str | None = None
    """Optional HF cache directory override."""

    output_dir: Path = Path("analysis/patterns")
    """Where to write YAML pattern files."""

    fallback: bool = False
    """Use fallback dataset if primary is unavailable."""

    dry_run: bool = False
    """If True, load samples but skip expensive analysis."""

    seed: int = 42
    """Random seed for sampling."""

    def resolve_dataset(self) -> str:
        """Return the dataset name, falling back if configured."""
        return self.dataset_name

    @property
    def is_wrapper_format(self) -> bool:
        """True if the dataset uses the wrapper (row_json) format."""
        return self.dataset_name in WRAPPER_DATASETS

    @property
    def patterns_output_dir(self) -> Path:
        """Shortcut for the output patterns directory."""
        return self.output_dir

    @property
    def stats_output_path(self) -> Path:
        """Path for the combined stats JSON file."""
        return self.output_dir / "combined_stats.json"


# Default singleton for convenience
DEFAULT_CONFIG: Final[AnalysisConfig] = AnalysisConfig()
