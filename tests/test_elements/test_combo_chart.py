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
