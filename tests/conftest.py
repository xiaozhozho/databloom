"""Shared pytest fixtures for excelreport tests."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Generator

import pandas as pd
import pytest

from excelreport.theme.base import Theme
from excelreport.theme.presets import (
    THEME_BUSINESS_BLUE,
    THEME_CLASSIC_WHITE,
    THEME_FRESH_GREEN,
    THEME_MINIMAL_GRAY,
    THEME_TECH_DARK,
    THEME_WARM_ORANGE,
)


@pytest.fixture
def temp_output_dir() -> Generator[Path, None, None]:
    """Temporary directory for output files that is cleaned after test."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_xlsx_path(temp_output_dir: Path) -> Path:
    """Path to a .xlsx file in the temp directory."""
    return temp_output_dir / "test_output.xlsx"


# ── Sample DataFrames ──────────────────────────────────────────────


@pytest.fixture
def df_simple() -> pd.DataFrame:
    """Simple 3-row DataFrame with numeric and text columns."""
    return pd.DataFrame(
        {
            "Product": ["Widget A", "Widget B", "Widget C"],
            "Sales": [15000, 23000, 18000],
            "Growth": [0.12, 0.08, 0.15],
        }
    )


@pytest.fixture
def df_wide() -> pd.DataFrame:
    """Wide DataFrame with many columns — tests horizontal layout."""
    data: dict[str, list] = {"Region": ["North", "South", "East", "West"]}
    for q in range(1, 5):
        data[f"Q{q} Revenue"] = [10000 + q * 2000 + i * 3000 for i in range(4)]
        data[f"Q{q} Cost"] = [5000 + q * 1000 + i * 1500 for i in range(4)]
        data[f"Q{q} Profit"] = [5000 + q * 1000 + i * 1500 for i in range(4)]
    return pd.DataFrame(data)


@pytest.fixture
def df_long() -> pd.DataFrame:
    """Long DataFrame with many rows — tests vertical layout."""
    months = pd.date_range("2025-01-01", periods=60, freq="ME")
    import numpy as np

    rng = np.random.default_rng(42)
    return pd.DataFrame(
        {
            "Date": months,
            "Revenue": rng.integers(50000, 150000, size=60),
            "Expenses": rng.integers(30000, 100000, size=60),
            "Customers": rng.integers(100, 500, size=60),
        }
    )


@pytest.fixture
def df_mixed_types() -> pd.DataFrame:
    """DataFrame with mixed data types: dates, numbers, text, categories."""
    return pd.DataFrame(
        {
            "Date": pd.date_range("2026-07-01", periods=10, freq="D"),
            "Category": ["Electronics", "Clothing", "Food", "Electronics", "Clothing",
                         "Food", "Electronics", "Clothing", "Food", "Electronics"],
            "Product": [f"Item-{i:02d}" for i in range(10)],
            "Quantity": [5, 12, 8, 3, 15, 9, 7, 11, 6, 4],
            "UnitPrice": [299.99, 49.50, 12.99, 399.00, 59.90, 15.50, 349.99, 45.00, 18.90, 279.00],
            "InStock": [True, True, False, True, False, True, True, False, True, False],
            "Rating": [4.5, 3.8, 4.2, 4.9, 3.5, 4.1, 4.7, 3.9, 4.3, 4.6],
        }
    )


@pytest.fixture
def df_empty() -> pd.DataFrame:
    """Empty DataFrame — edge case testing."""
    return pd.DataFrame()


@pytest.fixture
def df_single_row() -> pd.DataFrame:
    """Single row DataFrame — edge case."""
    return pd.DataFrame({"Name": ["Total"], "Value": [9999]})


@pytest.fixture
def df_all_numeric() -> pd.DataFrame:
    """All-numeric DataFrame — good for heatmaps and color scales."""
    import numpy as np

    rng = np.random.default_rng(7)
    data = rng.integers(10, 100, size=(8, 6))
    columns = [f"Metric_{chr(65 + i)}" for i in range(6)]
    return pd.DataFrame(data, columns=columns)


@pytest.fixture
def df_kpi() -> pd.DataFrame:
    """KPI-style summary data."""
    return pd.DataFrame(
        {
            "Metric": ["Total Revenue", "Total Cost", "Net Profit", "Profit Margin", "Customer Count"],
            "Current": [520000, 310000, 210000, 0.404, 1250],
            "Previous": [480000, 290000, 190000, 0.396, 1180],
            "Change%": [0.083, 0.069, 0.105, 0.020, 0.059],
        }
    )


@pytest.fixture
def df_time_series() -> pd.DataFrame:
    """Time series data — ideal for line/area charts."""
    dates = pd.date_range("2025-01-01", periods=24, freq="ME")
    import numpy as np

    rng = np.random.default_rng(123)
    base = rng.integers(1000, 5000, size=24).astype(float)
    return pd.DataFrame(
        {
            "Date": dates,
            "Product A": base + rng.normal(0, 200, 24).cumsum(),
            "Product B": base * 1.5 + rng.normal(0, 300, 24).cumsum(),
            "Product C": base * 0.8 + rng.normal(0, 150, 24).cumsum(),
        }
    )


# ── Theme fixtures ──────────────────────────────────────────────────


@pytest.fixture
def theme_business() -> Theme:
    return THEME_BUSINESS_BLUE


@pytest.fixture
def theme_fresh() -> Theme:
    return THEME_FRESH_GREEN


@pytest.fixture
def theme_tech() -> Theme:
    return THEME_TECH_DARK


@pytest.fixture
def theme_warm() -> Theme:
    return THEME_WARM_ORANGE


@pytest.fixture
def theme_minimal() -> Theme:
    return THEME_MINIMAL_GRAY


@pytest.fixture
def theme_classic() -> Theme:
    return THEME_CLASSIC_WHITE


@pytest.fixture
def all_themes() -> list[Theme]:
    return [
        THEME_BUSINESS_BLUE,
        THEME_FRESH_GREEN,
        THEME_TECH_DARK,
        THEME_WARM_ORANGE,
        THEME_MINIMAL_GRAY,
        THEME_CLASSIC_WHITE,
    ]
