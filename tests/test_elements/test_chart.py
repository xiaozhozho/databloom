"""Tests for ChartElement."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from excelreport.core.grid import Grid
from excelreport.core.workbook import WorkbookManager
from excelreport.elements.chart import ChartElement, _chart_category_col, _numeric_cols
from excelreport.theme.presets import THEME_BUSINESS_BLUE


class TestChartCategoryCol:
    """Tests for _chart_category_col auto-detection."""

    def test_datetime_first(self) -> None:
        df = pd.DataFrame(
            {
                "Date": pd.date_range("2026-01-01", periods=5),
                "Value": [1, 2, 3, 4, 5],
            }
        )
        assert _chart_category_col(df) == "Date"

    def test_string_fallback(self) -> None:
        df = pd.DataFrame(
            {
                "Name": ["A", "B", "C"],
                "Score": [10, 20, 30],
            }
        )
        assert _chart_category_col(df) == "Name"

    def test_first_column_fallback(self) -> None:
        df = pd.DataFrame(
            {
                "X": [1, 2, 3],
                "Y": [4, 5, 6],
            }
        )
        assert _chart_category_col(df) == "X"


class TestNumericCols:
    """Tests for _numeric_cols helper."""

    def test_filters_numeric(self) -> None:
        df = pd.DataFrame(
            {
                "Name": ["A", "B"],
                "Value": [10, 20],
                "Count": [5, 8],
            }
        )
        cols = _numeric_cols(df, "Name")
        assert "Value" in cols
        assert "Count" in cols
        assert "Name" not in cols


class TestChartElement:
    """Tests for ChartElement."""

    def test_measure_returns_reasonable_size(self, df_simple: pd.DataFrame) -> None:
        el = ChartElement(
            df_simple, chart_type="column", category_col="Product", value_cols=["Sales"]
        )
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        assert rows > 0
        assert cols > 0

    def test_needs_full_width(self, df_simple: pd.DataFrame) -> None:
        el = ChartElement(df_simple)
        assert el.needs_full_width() is True

    def test_auto_detect_category(self, df_time_series: pd.DataFrame) -> None:
        el = ChartElement(df_time_series)
        assert el.category_col == "Date"

    def test_auto_detect_value_cols(self, df_time_series: pd.DataFrame) -> None:
        el = ChartElement(df_time_series)
        assert "Product A" in el.value_cols
        assert "Product B" in el.value_cols
        assert "Date" not in el.value_cols

    def test_render_xlsxwriter_column_chart(
        self, temp_xlsx_path: Path, df_simple: pd.DataFrame
    ) -> None:
        """Render a column chart with xlsxwriter backend."""
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("Chart")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = ChartElement(
            df_simple,
            chart_type="column",
            category_col="Product",
            value_cols=["Sales"],
            title="Sales by Product",
        )
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), THEME_BUSINESS_BLUE)
        wm.close()
        assert temp_xlsx_path.stat().st_size > 0

    def test_render_xlsxwriter_line_chart(
        self, temp_xlsx_path: Path, df_time_series: pd.DataFrame
    ) -> None:
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("Line")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = ChartElement(
            df_time_series,
            chart_type="line",
            title="Time Series",
        )
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), THEME_BUSINESS_BLUE)
        wm.close()
        assert temp_xlsx_path.stat().st_size > 0

    def test_render_xlsxwriter_pie_chart(
        self, temp_xlsx_path: Path, df_simple: pd.DataFrame
    ) -> None:
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("Pie")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = ChartElement(
            df_simple,
            chart_type="pie",
            category_col="Product",
            value_cols=["Sales"],
        )
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), THEME_BUSINESS_BLUE)
        wm.close()
        assert temp_xlsx_path.stat().st_size > 0

    @pytest.mark.slow
    def test_render_matplotlib_column_chart(
        self, temp_xlsx_path: Path, df_simple: pd.DataFrame
    ) -> None:
        """Render using matplotlib backend."""
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("MPL")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = ChartElement(
            df_simple,
            chart_type="column",
            category_col="Product",
            value_cols=["Sales"],
            backend="matplotlib",
        )
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), THEME_BUSINESS_BLUE)
        wm.close()
        assert temp_xlsx_path.stat().st_size > 0

    @pytest.mark.slow
    def test_render_matplotlib_line_chart(
        self, temp_xlsx_path: Path, df_time_series: pd.DataFrame
    ) -> None:
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("MPL_Line")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = ChartElement(
            df_time_series,
            chart_type="line",
            backend="matplotlib",
        )
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), THEME_BUSINESS_BLUE)
        wm.close()
        assert temp_xlsx_path.stat().st_size > 0

    def test_chart_width_height_config(self, df_simple: pd.DataFrame) -> None:
        el = ChartElement(df_simple, chart_width=800, chart_height=500)
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        assert rows == 25  # 500 / 20
        assert cols == 13  # 800 / 60
