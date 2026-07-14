"""Tests for quick_report() — the one-liner API."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from excelreport import quick_report


class TestQuickReport:
    """Tests for quick_report function."""

    def test_returns_bytes_when_no_path(self, df_simple: pd.DataFrame) -> None:
        result = quick_report(df_simple)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_writes_file_when_path_given(
        self, df_simple: pd.DataFrame, temp_xlsx_path: Path
    ) -> None:
        result = quick_report(df_simple, output=temp_xlsx_path, title="Test")
        assert result is None
        assert temp_xlsx_path.exists()
        assert temp_xlsx_path.stat().st_size > 0

    def test_single_dataframe_with_theme(
        self, df_mixed_types: pd.DataFrame, temp_xlsx_path: Path
    ) -> None:
        quick_report(df_mixed_types, output=temp_xlsx_path, theme="tech_dark")
        assert temp_xlsx_path.exists()

    def test_multiple_dataframes(
        self, df_kpi: pd.DataFrame, df_time_series: pd.DataFrame, temp_xlsx_path: Path
    ) -> None:
        quick_report(df_kpi, df_time_series, output=temp_xlsx_path, title="Multi DF Report")
        assert temp_xlsx_path.exists()

    def test_no_dataframes(self) -> None:
        result = quick_report()
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_with_chart_type_specified(
        self, df_time_series: pd.DataFrame, temp_xlsx_path: Path
    ) -> None:
        quick_report(df_time_series, output=temp_xlsx_path, chart_type="line")
        assert temp_xlsx_path.exists()

    def test_all_themes_work(self, df_simple: pd.DataFrame) -> None:
        """Every built-in theme should work with quick_report."""
        for theme_name in [
            "business_blue",
            "fresh_green",
            "tech_dark",
            "warm_orange",
            "minimal_gray",
            "classic_white",
        ]:
            result = quick_report(df_simple, theme=theme_name)
            assert len(result) > 0, f"Theme {theme_name} failed"

    @pytest.mark.parametrize(
        "theme_name",
        [
            "business_blue",
            "fresh_green",
            "tech_dark",
            "warm_orange",
            "minimal_gray",
            "classic_white",
        ],
    )
    def test_theme_parametrized(self, df_simple: pd.DataFrame, theme_name: str) -> None:
        result = quick_report(df_simple, theme=theme_name)
        assert isinstance(result, bytes)

    def test_large_dataframe(self, df_long: pd.DataFrame) -> None:
        result = quick_report(df_long)
        assert len(result) > 0

    def test_wide_dataframe(self, df_wide: pd.DataFrame) -> None:
        result = quick_report(df_wide, title="Wide Report")
        assert len(result) > 0

    def test_kpi_data(self, df_kpi: pd.DataFrame) -> None:
        result = quick_report(df_kpi, title="KPI Dashboard")
        assert len(result) > 0

    def test_all_numeric_data(self, df_all_numeric: pd.DataFrame) -> None:
        result = quick_report(df_all_numeric, title="Numeric Data")
        assert len(result) > 0

    def test_from_plan_demo(self, temp_xlsx_path: Path) -> None:
        """Test the exact examples from the README/code-plan."""
        # Example 1: quick report
        df = pd.DataFrame(
            {
                "Product": ["Widget A", "Widget B", "Widget C"],
                "Sales": [15000, 23000, 18000],
                "Growth": [0.12, 0.08, 0.15],
            }
        )
        result = quick_report(df)
        assert isinstance(result, bytes)

        # Save to file
        quick_report(df, output=temp_xlsx_path, theme="business_blue")
        assert temp_xlsx_path.exists()
