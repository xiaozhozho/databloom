"""Tests for ChartElement."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from databloom.core.grid import Grid
from databloom.core.workbook import WorkbookManager
from databloom.elements.chart import ChartElement, _chart_category_col, _numeric_cols
from databloom.theme.presets import THEME_BUSINESS_BLUE


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

    def test_categorical_dtype_detection(self) -> None:
        """Tests: CategoricalDtype column is detected ahead of first-column fallback.

        How: Create DataFrame with integer-coded categories (so is_string_dtype
             does NOT match), forcing the loop to reach the isinstance check
             before falling through to the first-column default.
        Why: Categorical columns make natural chart categories.  Using integer
             categories avoids the string-dtype short-circuit so the explicit
             ``isinstance(dtype, pd.CategoricalDtype)`` branch is exercised.
        """
        df = pd.DataFrame(
            {
                "Group": pd.Categorical([1, 2, 3, 1, 2, 3]),
                "Score": [10, 20, 30, 40, 50, 60],
            }
        )
        assert _chart_category_col(df) == "Group"


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

    # ── xlsxwriter: doughnut, radar, stock charts ──────────────────────

    def test_render_xlsxwriter_doughnut_chart(
        self, temp_xlsx_path: Path, df_simple: pd.DataFrame
    ) -> None:
        """Tests: Doughnut chart renders via xlsxwriter backend without error.

        How: Create a ChartElement with chart_type="doughnut", render it to a temp
             workbook, and verify the output file is produced.
        Why: Covers the chart.set_hole_size(40) branch at line 160 that is specific
             to doughnut charts.
        """
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("Doughnut")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = ChartElement(
            df_simple,
            chart_type="doughnut",
            category_col="Product",
            value_cols=["Sales"],
            title="Sales Distribution",
        )
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), THEME_BUSINESS_BLUE)
        wm.close()
        assert temp_xlsx_path.stat().st_size > 0

    def test_render_xlsxwriter_radar_chart(
        self, temp_xlsx_path: Path, df_simple: pd.DataFrame
    ) -> None:
        """Tests: Radar chart renders via xlsxwriter backend without error.

        How: Create a ChartElement with chart_type="radar", render to temp workbook,
             and verify output file is created.
        Why: Covers the xlsxwriter radar chart code path; radar is one of the
             native xlsxwriter chart types with zero special-casing in _render_xlsxwriter.
        """
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("Radar")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = ChartElement(
            df_simple,
            chart_type="radar",
            category_col="Product",
            value_cols=["Sales", "Growth"],
            title="Product Comparison Radar",
        )
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), THEME_BUSINESS_BLUE)
        wm.close()
        assert temp_xlsx_path.stat().st_size > 0

    def test_render_xlsxwriter_stock_chart(
        self, temp_xlsx_path: Path, df_simple: pd.DataFrame
    ) -> None:
        """Tests: Stock chart renders via xlsxwriter backend without error.

        How: Create a ChartElement with chart_type="stock", render to temp workbook,
             and verify output file is created.
        Why: Covers the xlsxwriter stock chart code path; stock is a native
             xlsxwriter chart type with no special-casing in _render_xlsxwriter.
        """
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("Stock")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = ChartElement(
            df_simple,
            chart_type="stock",
            category_col="Product",
            value_cols=["Sales", "Growth"],
            title="Stock Trend",
        )
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), THEME_BUSINESS_BLUE)
        wm.close()
        assert temp_xlsx_path.stat().st_size > 0

    # ── matplotlib: area, scatter, pie, doughnut, radar, stock, bar charts ──

    @pytest.mark.slow
    def test_render_matplotlib_area_chart(
        self, temp_xlsx_path: Path, df_time_series: pd.DataFrame
    ) -> None:
        """Tests: Area chart renders via matplotlib backend without error.

        How: Render an area chart with time-series data using matplotlib backend
             and verify the output file is produced.
        Why: Covers the fill_between area chart branch (lines 327-333) that was
             previously uncovered.
        """
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("MPL_Area")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = ChartElement(
            df_time_series,
            chart_type="area",
            backend="matplotlib",
            title="Area Trend",
        )
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), THEME_BUSINESS_BLUE)
        wm.close()
        assert temp_xlsx_path.stat().st_size > 0

    @pytest.mark.slow
    def test_render_matplotlib_scatter_chart(
        self, temp_xlsx_path: Path, df_simple: pd.DataFrame
    ) -> None:
        """Tests: Scatter chart renders via matplotlib backend without error.

        How: Render a scatter chart using matplotlib backend and verify output.
        Why: Covers the scatter chart branch (lines 334-342) that was previously
             uncovered.
        """
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("MPL_Scatter")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = ChartElement(
            df_simple,
            chart_type="scatter",
            category_col="Product",
            value_cols=["Sales", "Growth"],
            backend="matplotlib",
            title="Scatter Plot",
        )
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), THEME_BUSINESS_BLUE)
        wm.close()
        assert temp_xlsx_path.stat().st_size > 0

    @pytest.mark.slow
    def test_render_matplotlib_pie_chart(
        self, temp_xlsx_path: Path, df_simple: pd.DataFrame
    ) -> None:
        """Tests: Pie chart renders via matplotlib backend without error.

        How: Render a pie chart using matplotlib backend and verify output.
        Why: Covers the pie chart branch (lines 317-326) that was previously
             uncovered, including ax.pie() and ax.axis("equal").
        """
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("MPL_Pie")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = ChartElement(
            df_simple,
            chart_type="pie",
            category_col="Product",
            value_cols=["Sales"],
            backend="matplotlib",
            title="Product Share",
        )
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), THEME_BUSINESS_BLUE)
        wm.close()
        assert temp_xlsx_path.stat().st_size > 0

    @pytest.mark.slow
    def test_render_matplotlib_doughnut_chart(
        self, temp_xlsx_path: Path, df_simple: pd.DataFrame
    ) -> None:
        """Tests: Doughnut chart renders via matplotlib backend without error.

        How: Render a doughnut chart using matplotlib backend and verify output.
        Why: Covers the doughnut chart branch (lines 343-353) including the
             wedgeprops={"width": 0.4} donut hole configuration.
        """
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("MPL_Doughnut")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = ChartElement(
            df_simple,
            chart_type="doughnut",
            category_col="Product",
            value_cols=["Sales"],
            backend="matplotlib",
            title="Sales Doughnut",
        )
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), THEME_BUSINESS_BLUE)
        wm.close()
        assert temp_xlsx_path.stat().st_size > 0

    @pytest.mark.slow
    def test_render_matplotlib_bar_chart(
        self, temp_xlsx_path: Path, df_simple: pd.DataFrame
    ) -> None:
        """Tests: Horizontal bar chart renders via matplotlib backend without error.

        How: Render a bar (horizontal) chart via matplotlib and verify output.
        Why: Covers the bar chart branch (lines 296-305) including ax.barh()
             that was previously uncovered.
        """
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("MPL_Bar")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = ChartElement(
            df_simple,
            chart_type="bar",
            category_col="Product",
            value_cols=["Sales"],
            backend="matplotlib",
            title="Horizontal Bar",
        )
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), THEME_BUSINESS_BLUE)
        wm.close()
        assert temp_xlsx_path.stat().st_size > 0

    @pytest.mark.slow
    def test_render_matplotlib_radar_chart(
        self, temp_xlsx_path: Path, df_simple: pd.DataFrame
    ) -> None:
        """Tests: Radar chart renders via matplotlib backend without error.

        How: Render a radar chart via matplotlib and verify output.
             Radar needs at least 3 points to form a closed polygon.
        Why: Covers the radar chart branch (lines 354-362) including polygon
             fill, linspace angle computation, and polar coordinate setup.
        """
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("MPL_Radar")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = ChartElement(
            df_simple,
            chart_type="radar",
            category_col="Product",
            value_cols=["Sales", "Growth"],
            backend="matplotlib",
            title="Skills Radar",
        )
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), THEME_BUSINESS_BLUE)
        wm.close()
        assert temp_xlsx_path.stat().st_size > 0

    @pytest.mark.slow
    def test_render_matplotlib_stock_chart(
        self, temp_xlsx_path: Path, df_simple: pd.DataFrame
    ) -> None:
        """Tests: Stock chart renders via matplotlib backend without error.

        How: Render a stock chart via matplotlib and verify output.
        Why: Covers the stock chart branch (lines 363-374) including the
             alternating up/down axvspan visualization.
        """
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("MPL_Stock")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = ChartElement(
            df_simple,
            chart_type="stock",
            category_col="Product",
            value_cols=["Sales"],
            backend="matplotlib",
            title="Stock Price",
        )
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), THEME_BUSINESS_BLUE)
        wm.close()
        assert temp_xlsx_path.stat().st_size > 0

    # ── xlsxwriter: area, scatter, bar native charts ──────────────────

    def test_render_xlsxwriter_area_chart(
        self, temp_xlsx_path: Path, df_time_series: pd.DataFrame
    ) -> None:
        """Tests: Area chart renders via xlsxwriter backend without error.

        How: Render an area chart using xlsxwriter native backend and verify output.
        Why: Covers the area chart code path through xlsxwriter backend.
        """
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("Area")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = ChartElement(
            df_time_series,
            chart_type="area",
            title="Area Trend",
        )
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), THEME_BUSINESS_BLUE)
        wm.close()
        assert temp_xlsx_path.stat().st_size > 0

    def test_render_xlsxwriter_scatter_chart(
        self, temp_xlsx_path: Path, df_simple: pd.DataFrame
    ) -> None:
        """Tests: Scatter chart renders via xlsxwriter backend without error.

        How: Render a scatter chart using xlsxwriter native backend and verify output.
        Why: Covers the scatter chart code path through xlsxwriter backend.
        """
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("Scatter")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = ChartElement(
            df_simple,
            chart_type="scatter",
            category_col="Product",
            value_cols=["Sales", "Growth"],
            title="Scatter XY",
        )
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), THEME_BUSINESS_BLUE)
        wm.close()
        assert temp_xlsx_path.stat().st_size > 0

    def test_render_xlsxwriter_bar_chart(
        self, temp_xlsx_path: Path, df_simple: pd.DataFrame
    ) -> None:
        """Tests: Horizontal bar chart renders via xlsxwriter backend without error.

        How: Render a bar chart using xlsxwriter native backend and verify output.
        Why: Covers the bar chart code path through xlsxwriter backend.
        """
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("Bar")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = ChartElement(
            df_simple,
            chart_type="bar",
            category_col="Product",
            value_cols=["Sales"],
            title="Horizontal Bar",
        )
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), THEME_BUSINESS_BLUE)
        wm.close()
        assert temp_xlsx_path.stat().st_size > 0

    # ── Edge cases ─────────────────────────────────────────────────────

    def test_render_matplotlib_single_value_col_legend_skip(
        self, temp_xlsx_path: Path, df_simple: pd.DataFrame
    ) -> None:
        """Tests: Matplotlib does not render legend when only one value column exists.

        How: Render a column chart with a single value column via matplotlib.
             The legend block (lines 376-380) is skipped when len(value_cols) <= 1.
        Why: Ensures the legend-suppression branch for single-series charts is exercised.
        """
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("MPL_NoLegend")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = ChartElement(
            df_simple,
            chart_type="column",
            category_col="Product",
            value_cols=["Sales"],
            backend="matplotlib",
            title="Single Series",
        )
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), THEME_BUSINESS_BLUE)
        wm.close()
        assert temp_xlsx_path.stat().st_size > 0

    def test_needs_full_width_override(self, df_simple: pd.DataFrame) -> None:
        """Tests: full_width=False is respected.

        How: Create a ChartElement with full_width=False and verify needs_full_width
             returns False.
        Why: Covers the _full_width value propagation through needs_full_width.
        """
        el = ChartElement(df_simple, full_width=False)
        assert el.needs_full_width() is False
