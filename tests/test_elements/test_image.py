"""Tests for ImageElement."""

from __future__ import annotations

# Create a tiny valid PNG for testing
import struct
import zlib
from pathlib import Path

import pytest

from excelreport.core.grid import Grid
from excelreport.core.workbook import WorkbookManager
from excelreport.elements.image import ImageElement
from excelreport.theme.presets import THEME_BUSINESS_BLUE


def _make_tiny_png() -> bytes:
    """Create a minimal valid PNG file in memory."""

    def chunk(chunk_type: bytes, data: bytes) -> bytes:
        c = chunk_type + data
        crc = struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
        return struct.pack(">I", len(data)) + c + crc

    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
    idat = chunk(b"IDAT", zlib.compress(b"\x00\xff\x00\x00"))
    iend = chunk(b"IEND", b"")
    return signature + ihdr + idat + iend


@pytest.fixture
def tiny_png_path(tmp_path: Path) -> Path:
    p = tmp_path / "tiny.png"
    p.write_bytes(_make_tiny_png())
    return p


class TestImageElement:
    """Tests for ImageElement."""

    def test_measure_defaults(self) -> None:
        el = ImageElement("chart.png")
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        assert rows == 15
        assert cols == 10

    def test_measure_with_hints(self) -> None:
        el = ImageElement("chart.png", height_hint=20, width_hint=15)
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        assert rows == 20
        assert cols == 15

    def test_needs_full_width_false(self) -> None:
        assert ImageElement("x.png").needs_full_width() is False

    def test_render_inserts_image(self, temp_xlsx_path: Path, tiny_png_path: Path) -> None:
        wm = WorkbookManager(temp_xlsx_path)
        ws = wm.add_sheet("Img")
        grid = Grid(margin_top=0, margin_left=0, spacing=0)
        el = ImageElement(tiny_png_path, scale_x=0.5, scale_y=0.5)
        rows, cols = el.measure(THEME_BUSINESS_BLUE)
        el.render(wm, ws, grid.place(0, 0, rows=rows, cols=cols), THEME_BUSINESS_BLUE)
        wm.close()
        assert temp_xlsx_path.stat().st_size > 0
