"""Tests for the ComboChartElement."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from databloom.elements.chart import ComboChartElement


class TestComboChartElement:
    """Tests for combo chart (column + line dual Y-axis)."""

    @pytest.fixture
    def combo_df(self) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "Month": ["Jan", "Feb", "Mar", "Apr", "May"],
                "Revenue": [1000, 1200, 1100, 1400, 1300],
                "Cost": [600, 700, 680, 800, 750],
                "Margin": [0.35, 0.38, 0.35, 0.40, 0.39],
            }
        )

    def test_init_defaults(self, combo_df: pd.DataFrame) -> None:
        el = ComboChartElement(combo_df)
        assert el.chart_width == 640
        assert el.chart_height == 400
        assert el._full_width is True

    def test_measure(self, combo_df: pd.DataFrame) -> None:
        from databloom.theme.presets import get_theme

        el = ComboChartElement(combo_df)
        rows, cols = el.measure(get_theme("business_blue"))
        assert rows > 0
        assert cols > 0

    def test_init_with_custom_cols(self, combo_df: pd.DataFrame) -> None:
        el = ComboChartElement(
            combo_df,
            category_col="Month",
            bar_cols=["Revenue", "Cost"],
            line_cols=["Margin"],
            bar_title="Revenue & Cost",
            line_title="Margin %",
            title="Test Combo",
        )
        assert el.bar_cols == ["Revenue", "Cost"]
        assert el.line_cols == ["Margin"]
        assert el.bar_title == "Revenue & Cost"
        assert el.line_title == "Margin %"
        assert el.title == "Test Combo"

    def test_needs_full_width(self, combo_df: pd.DataFrame) -> None:
        el = ComboChartElement(combo_df)
        assert el.needs_full_width() is True

        el2 = ComboChartElement(combo_df, full_width=False)
        assert el2.needs_full_width() is False

    def test_render_to_file(self, combo_df: pd.DataFrame, temp_xlsx_path: Path) -> None:
        from databloom.core.grid import Grid
        from databloom.core.workbook import WorkbookManager
        from databloom.theme.presets import get_theme

        theme = get_theme("business_blue")
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("Combo")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = ComboChartElement(
            combo_df,
            category_col="Month",
            bar_cols=["Revenue", "Cost"],
            line_cols=["Margin"],
            title="Revenue vs Margin",
        )
        rows, cols = el.measure(theme)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), theme)
        wm.close()
        assert temp_xlsx_path.stat().st_size > 0

    def test_render_with_axis_titles(
        self, combo_df: pd.DataFrame, temp_xlsx_path: Path
    ) -> None:
        """Tests: Combo chart renders with bar and line axis titles set.

        How: Create a ComboChartElement with both bar_title and line_title,
             render to a temp workbook, and verify the output file is created.
        Why: Covers the y_axis["name"] and y2_axis["name"] assignment branches
             (lines 618, 620) that are skipped when axis titles are empty strings.
        """
        from databloom.core.grid import Grid
        from databloom.core.workbook import WorkbookManager
        from databloom.theme.presets import get_theme

        theme = get_theme("business_blue")
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("ComboAxis")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = ComboChartElement(
            combo_df,
            category_col="Month",
            bar_cols=["Revenue", "Cost"],
            line_cols=["Margin"],
            bar_title="Revenue & Cost (¥)",
            line_title="Margin (%)",
            title="Revenue vs Margin",
        )
        rows, cols = el.measure(theme)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), theme)
        wm.close()
        assert temp_xlsx_path.stat().st_size > 0

    def test_render_combo_no_title(
        self, combo_df: pd.DataFrame, temp_xlsx_path: Path
    ) -> None:
        """Tests: Combo chart renders with no overall title.

        How: Create a ComboChartElement without title, render and verify.
        Why: Covers the branch where chart.set_title is skipped when title is empty.
        """
        from databloom.core.grid import Grid
        from databloom.core.workbook import WorkbookManager
        from databloom.theme.presets import get_theme

        theme = get_theme("business_blue")
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("ComboNoTitle")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = ComboChartElement(
            combo_df,
            category_col="Month",
            bar_cols=["Revenue", "Cost"],
            line_cols=["Margin"],
        )
        rows, cols = el.measure(theme)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), theme)
        wm.close()
        assert temp_xlsx_path.stat().st_size > 0

    def test_render_combo_bar_only(
        self, combo_df: pd.DataFrame, temp_xlsx_path: Path
    ) -> None:
        """Tests: Combo chart with only bars (no line series) renders without error.

        How: Create a ComboChartElement without line_cols and render.
        Why: Covers the branch where the line_chart combine block (line 587-615)
             is skipped because line_cols is empty.
        """
        from databloom.core.grid import Grid
        from databloom.core.workbook import WorkbookManager
        from databloom.theme.presets import get_theme

        theme = get_theme("business_blue")
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("ComboBarOnly")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = ComboChartElement(
            combo_df,
            category_col="Month",
            bar_cols=["Revenue", "Cost"],
            line_cols=[],
        )
        rows, cols = el.measure(theme)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), theme)
        wm.close()
        assert temp_xlsx_path.stat().st_size > 0
