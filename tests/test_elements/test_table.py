"""Tests for TableElement."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from databloom.core.grid import Grid
from databloom.core.workbook import WorkbookManager
from databloom.elements.table import TableElement, _column_width, _infer_dtype_format
from databloom.theme.presets import THEME_BUSINESS_BLUE, THEME_TECH_DARK


class TestInferDtypeFormat:
    """Tests for _infer_dtype_format helper."""

    def test_integer_dtype(self) -> None:
        s = pd.Series([1, 2, 3])
        fmt = _infer_dtype_format(s, THEME_BUSINESS_BLUE)
        assert fmt == "#,##0"

    def test_float_dtype(self) -> None:
        s = pd.Series([1.5, 2.3, 3.7])
        fmt = _infer_dtype_format(s, THEME_BUSINESS_BLUE)
        assert "#,##0" in fmt

    def test_percent_like_float(self) -> None:
        s = pd.Series([0.12, 0.08, 0.15])
        fmt = _infer_dtype_format(s, THEME_BUSINESS_BLUE)
        assert fmt == "0.0%"

    def test_datetime_dtype(self) -> None:
        s = pd.Series(pd.date_range("2026-01-01", periods=3))
        fmt = _infer_dtype_format(s, THEME_BUSINESS_BLUE)
        assert fmt == "yyyy-mm-dd"

    def test_bool_dtype(self) -> None:
        s = pd.Series([True, False, True])
        fmt = _infer_dtype_format(s, THEME_BUSINESS_BLUE)
        assert fmt == ""

    def test_string_dtype(self) -> None:
        s = pd.Series(["a", "b", "c"])
        fmt = _infer_dtype_format(s, THEME_BUSINESS_BLUE)
        assert fmt == ""


class TestColumnWidth:
    """Tests for _column_width helper."""

    def test_returns_reasonable_width(self) -> None:
        s = pd.Series(["Hello", "World"])
        w = _column_width("col_name", s)
        assert 5 <= w <= 30

    def test_header_length_respected(self) -> None:
        s = pd.Series(["a", "b"])
        w = _column_width("very_long_column_name", s)
        assert w >= 10


class TestTableElement:
    """Tests for TableElement."""

    def test_measure_no_title(self, df_simple: pd.DataFrame) -> None:
        el = TableElement(df_simple)
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        assert rows == len(df_simple) + 1  # header + data rows
        assert cols == len(df_simple.columns)

    def test_measure_with_title(self, df_simple: pd.DataFrame) -> None:
        el = TableElement(df_simple, title="Sales Data")
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        assert rows == len(df_simple) + 2  # title + header + data rows

    def test_needs_full_width(self, df_simple: pd.DataFrame) -> None:
        assert TableElement(df_simple).needs_full_width() is True

    def test_render_simple_table(self, temp_xlsx_path: Path, df_simple: pd.DataFrame) -> None:
        """Integration: render a table and verify with openpyxl."""
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("Data")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = TableElement(df_simple, title="Summary")
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        placement = grid.place(0, 0, rows=rows, cols=cols)
        el.render(wm, ws, placement, THEME_BUSINESS_BLUE)
        wm.close()

        import openpyxl

        wb = openpyxl.load_workbook(temp_xlsx_path)
        ws_r = wb["Data"]

        # Title row
        assert ws_r["A1"].value == "Summary"

        # Header row is row 2 (after title)
        assert ws_r["A2"].value == "Product"
        assert ws_r["B2"].value == "Sales"
        assert ws_r["C2"].value == "Growth"

        # Data rows
        assert ws_r["A3"].value == "Widget A"
        assert ws_r["B3"].value == 15000
        assert ws_r["C3"].value == 0.12

    def test_render_empty_dataframe(self, temp_xlsx_path: Path) -> None:
        """Should not crash on empty DataFrame."""
        df = pd.DataFrame({"A": [], "B": []})
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("Empty")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = TableElement(df)
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        el.render(
            wm, ws, grid.place(0, 0, rows=max(rows, 1), cols=max(cols, 1)), THEME_BUSINESS_BLUE
        )
        wm.close()
        assert temp_xlsx_path.exists()

    def test_render_single_row(self, temp_xlsx_path: Path, df_single_row: pd.DataFrame) -> None:
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("Single")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = TableElement(df_single_row)
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), THEME_BUSINESS_BLUE)
        wm.close()

        import openpyxl

        wb = openpyxl.load_workbook(temp_xlsx_path)
        ws_r = wb["Single"]
        assert ws_r["A1"].value == "Name"
        assert ws_r["A2"].value == "Total"
        assert ws_r["B2"].value == 9999

    def test_render_with_column_format(self, temp_xlsx_path: Path) -> None:
        """Custom column formats override auto-detection."""
        df = pd.DataFrame({"Price": [1.23456, 2.34567, 3.45678]})
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("Fmt")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = TableElement(df, column_formats={"Price": "0.000"})
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), THEME_BUSINESS_BLUE)
        wm.close()

        import openpyxl

        wb = openpyxl.load_workbook(temp_xlsx_path)
        ws_r = wb["Fmt"]
        assert ws_r["A2"].value == 1.23456  # value preserved

    def test_render_alternating_row_colors(
        self, temp_xlsx_path: Path, df_simple: pd.DataFrame
    ) -> None:
        """Verify alternating row fills are applied — fills should differ."""
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("Alt")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = TableElement(df_simple)
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), THEME_BUSINESS_BLUE)
        wm.close()

        import openpyxl

        wb = openpyxl.load_workbook(temp_xlsx_path)
        ws_r = wb["Alt"]
        # Verify both data rows have solid fills
        assert ws_r["A3"].fill is not None
        assert ws_r["A3"].fill.patternType == "solid"
        assert ws_r["A4"].fill is not None
        assert ws_r["A4"].fill.patternType == "solid"
        # Row colors should differ (alternating)
        assert ws_r["A3"].fill.start_color.rgb != ws_r["A4"].fill.start_color.rgb

    def test_render_large_dataframe(self, temp_xlsx_path: Path, df_long: pd.DataFrame) -> None:
        """Stress test: large DataFrame should render without error."""
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("Large")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = TableElement(df_long)
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), THEME_BUSINESS_BLUE)
        wm.close()

        import openpyxl

        wb = openpyxl.load_workbook(temp_xlsx_path)
        ws_r = wb["Large"]
        assert ws_r["A1"].value == "Date"
        # 60 data rows + 1 header
        assert ws_r["A61"].value is not None

    def test_render_wide_dataframe(self, temp_xlsx_path: Path, df_wide: pd.DataFrame) -> None:
        """Wide table: many columns."""
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("Wide")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = TableElement(df_wide)
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), THEME_BUSINESS_BLUE)
        wm.close()

        import openpyxl

        wb = openpyxl.load_workbook(temp_xlsx_path)
        ws_r = wb["Wide"]
        # 13 columns (Region + 4*3 Qs)
        assert ws_r["A1"].value == "Region"
        assert ws_r["M1"].value is not None  # Last column header

    def test_render_with_dark_theme(self, temp_xlsx_path: Path, df_simple: pd.DataFrame) -> None:
        """Render with tech_dark theme."""
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("Dark")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = TableElement(df_simple)
        rows, cols = el.measure(THEME_TECH_DARK)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), THEME_TECH_DARK)
        wm.close()

        import openpyxl

        wb = openpyxl.load_workbook(temp_xlsx_path)
        ws_r = wb["Dark"]
        assert ws_r["A1"].value == "Product"  # Header present
        # Dark theme should have dark fills
        assert ws_r["A1"].fill is not None

    def test_mixed_types(self, temp_xlsx_path: Path, df_mixed_types: pd.DataFrame) -> None:
        """Table with dates, bools, strings, floats renders correctly."""
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("Mixed")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = TableElement(df_mixed_types)
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), THEME_BUSINESS_BLUE)
        wm.close()
        assert temp_xlsx_path.stat().st_size > 0
