"""
Load real-world test datasets for databloom testing.

Datasets are cached as a single pickle file for fast reload.
The pickle itself is large (8.9 MB) and excluded from git via .gitignore.

Usage::

    import sys; sys.path.insert(0, 'tests')
    from test_data import load_test_datasets, list_datasets

    data = load_test_datasets()
    ecom = data["e_commerce_10k"]
    aw_sales = data["adventure_works_sales"]
    coffee = data["beverage_retailer"]
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

_PICKLE_PATH = Path(__file__).resolve().parent / "datasets" / "test_datasets.pkl"


def load_test_datasets() -> dict[str, Any]:
    """Load all standardised test datasets.

    Returns:
        Dict mapping dataset name to clean pandas DataFrame.
    """
    with open(_PICKLE_PATH, "rb") as f:
        raw: dict[str, dict[str, Any]] = pickle.load(f)
    return {name: info["df"] for name, info in raw.items()}


def load_dataset(name: str) -> Any:
    """Load a single dataset by name.

    Args:
        name: One of ``"e_commerce_10k"``, ``"adventure_works_sales"``,
            ``"beverage_retailer"``.

    Returns:
        The requested DataFrame.

    Raises:
        KeyError: If the name is not recognised.
    """
    with open(_PICKLE_PATH, "rb") as f:
        raw: dict[str, dict[str, Any]] = pickle.load(f)
    if name not in raw:
        available = list(raw.keys())
        raise KeyError(f"Unknown dataset {name!r}. Available: {available}")
    return raw[name]["df"]


def list_datasets() -> list[str]:
    """Return available dataset names."""
    with open(_PICKLE_PATH, "rb") as f:
        raw: dict[str, dict[str, Any]] = pickle.load(f)
    return list(raw.keys())


def dataset_info(name: str) -> dict[str, Any]:
    """Return metadata for a dataset (excluding the DataFrame)."""
    with open(_PICKLE_PATH, "rb") as f:
        raw: dict[str, dict[str, Any]] = pickle.load(f)
    if name not in raw:
        available = list(raw.keys())
        raise KeyError(f"Unknown dataset {name!r}. Available: {available}")
    result = {k: v for k, v in raw[name].items() if k != "df"}
    result["shape"] = raw[name]["df"].shape
    return result
