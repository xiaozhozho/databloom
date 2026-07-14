"""Tests for WorkbookManager and FormatCache."""

from __future__ import annotations

import io
from pathlib import Path

import pytest
import xlsxwriter

from excelreport.core.workbook import FormatCache, WorkbookManager


class TestFormatCache:
    """Tests for FormatCache."""

    def test_get_creates_format(self) -> None:
        wb = xlsxwriter.Workbook(io.BytesIO(), {"in_memory": True})
        cache = FormatCache()
        fmt = cache.get(wb, bold=True, font_size=14)
        assert fmt is not None
        wb.close()

    def test_same_kwargs_returns_same_format(self) -> None:
        wb = xlsxwriter.Workbook(io.BytesIO(), {"in_memory": True})
        cache = FormatCache()
        f1 = cache.get(wb, bold=True, font_name="Arial", font_size=11)
        f2 = cache.get(wb, bold=True, font_size=11, font_name="Arial")
        assert f1 is f2  # same object returned from cache
        wb.close()

    def test_different_kwargs_returns_different_format(self) -> None:
        wb = xlsxwriter.Workbook(io.BytesIO(), {"in_memory": True})
        cache = FormatCache()
        f1 = cache.get(wb, bold=True)
        f2 = cache.get(wb, bold=False)
        assert f1 is not f2
        wb.close()


class TestWorkbookManager:
    """Tests for WorkbookManager."""

    def test_create_with_path(self, temp_xlsx_path: Path) -> None:
        wm = WorkbookManager(temp_xlsx_path)
        assert wm._output == temp_xlsx_path
        assert wm._buffer is None
        assert wm.sheet_count == 0
        wm.close()

    def test_create_without_path_writes_to_buffer(self) -> None:
        wm = WorkbookManager()
        assert wm._output is None
        assert wm._buffer is not None
        wm.close()

    def test_close_returns_bytes_when_no_path(self) -> None:
        wm = WorkbookManager()
        ws = wm.add_sheet("Test")
        ws.write(0, 0, "hello")
        data = wm.close()
        assert isinstance(data, bytes)
        assert len(data) > 0

    def test_close_returns_none_when_path_given(self, temp_xlsx_path: Path) -> None:
        wm = WorkbookManager(temp_xlsx_path)
        wm.add_sheet("Data")
        result = wm.close()
        assert result is None
        assert temp_xlsx_path.exists()
        assert temp_xlsx_path.stat().st_size > 0

    def test_add_sheet_creates_worksheet(self, temp_xlsx_path: Path) -> None:
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("Overview")
        assert ws is not None
        assert wm.has_sheet("Overview") is True
        assert wm.sheet_count == 1
        wm.close()

    def test_add_sheet_duplicate_name_raises(self, temp_xlsx_path: Path) -> None:
        wm = WorkbookManager(temp_xlsx_path)
        wm.add_sheet("Data")
        with pytest.raises(ValueError, match="already exists"):
            wm.add_sheet("Data")
        wm.close()

    def test_get_sheet_returns_existing(self, temp_xlsx_path: Path) -> None:
        wm = WorkbookManager(temp_xlsx_path)
        ws1 = wm.add_sheet("Metrics")
        ws2 = wm.get_sheet("Metrics")
        assert ws1 is ws2
        wm.close()

    def test_get_sheet_missing_raises_keyerror(self, temp_xlsx_path: Path) -> None:
        wm = WorkbookManager(temp_xlsx_path)
        with pytest.raises(KeyError, match="not found"):
            wm.get_sheet("Missing")
        wm.close()

    def test_has_sheet_false_for_unknown(self, temp_xlsx_path: Path) -> None:
        wm = WorkbookManager(temp_xlsx_path)
        assert wm.has_sheet("Nope") is False
        wm.close()

    def test_sheet_count_tracks_additions(self, temp_xlsx_path: Path) -> None:
        wm = WorkbookManager(temp_xlsx_path)
        assert wm.sheet_count == 0
        wm.add_sheet("A")
        assert wm.sheet_count == 1
        wm.add_sheet("B")
        wm.add_sheet("C")
        assert wm.sheet_count == 3
        wm.close()

    def test_context_manager(self, temp_xlsx_path: Path) -> None:
        with WorkbookManager(temp_xlsx_path) as wm:
            ws = wm.add_sheet("Data")
            ws.write(0, 0, "x")
        assert temp_xlsx_path.exists()

    def test_close_is_idempotent(self) -> None:
        wm = WorkbookManager()
        wm.add_sheet("X")
        r1 = wm.close()
        r2 = wm.close()
        assert r1 is not None
        assert r2 is None  # second close is a no-op

    def test_format_cache_is_shared(self, temp_xlsx_path: Path) -> None:
        wm = WorkbookManager(temp_xlsx_path)
        assert isinstance(wm.format_cache, FormatCache)
        fmt1 = wm.format_cache.get(wm.wb, bold=True)
        fmt2 = wm.format_cache.get(wm.wb, bold=True)
        assert fmt1 is fmt2
        wm.close()

    def test_multiple_sheets_independent(self, temp_xlsx_path: Path) -> None:
        wm = WorkbookManager(temp_xlsx_path)
        s1 = wm.add_sheet("Sheet1")
        s2 = wm.add_sheet("Sheet2")
        s1.write(0, 0, "One")
        s2.write(0, 0, "Two")
        assert wm.sheet_count == 2
        wm.close()

    def test_output_directory_auto_created(self, temp_output_dir: Path) -> None:
        nested = temp_output_dir / "reports" / "2026" / "output.xlsx"
        wm = WorkbookManager(nested)
        wm.add_sheet("D")
        wm.close()
        assert nested.exists()
