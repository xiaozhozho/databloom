"""Tests for Theme dataclass and style specifications."""

from __future__ import annotations

from excelreport.theme.base import (
    BorderSpec,
    FillSpec,
    FontSpec,
    ParagraphStyle,
    SubtitleStyle,
    TableStyle,
    Theme,
    TitleStyle,
)


class TestFontSpec:
    """Tests for FontSpec dataclass."""

    def test_default_values(self) -> None:
        font = FontSpec()
        assert font.name == "Arial"
        assert font.size == 11
        assert font.bold is False
        assert font.italic is False
        assert font.color == "#000000"
        assert font.underline is False

    def test_custom_values(self) -> None:
        font = FontSpec(name="Calibri", size=14, bold=True, italic=True, color="#FF0000")
        assert font.name == "Calibri"
        assert font.size == 14
        assert font.bold is True
        assert font.color == "#FF0000"

    def test_equality(self) -> None:
        f1 = FontSpec(name="Arial", size=11)
        f2 = FontSpec(name="Arial", size=11)
        f3 = FontSpec(name="Arial", size=12)
        assert f1 == f2
        assert f1 != f3


class TestFillSpec:
    """Tests for FillSpec dataclass."""

    def test_default_values(self) -> None:
        fill = FillSpec()
        assert fill.color == "#FFFFFF"
        assert fill.pattern == 1

    def test_custom_color(self) -> None:
        fill = FillSpec(color="#2F5496")
        assert fill.color == "#2F5496"


class TestBorderSpec:
    """Tests for BorderSpec dataclass."""

    def test_default_values(self) -> None:
        border = BorderSpec()
        assert border.style == 1
        assert border.color == "#D9D9D9"


class TestTableStyle:
    """Tests for TableStyle dataclass."""

    def test_default_creates_valid_style(self) -> None:
        ts = TableStyle()
        assert ts.header_font.bold is True
        assert ts.header_font.size == 11
        assert ts.data_font.size == 10
        assert isinstance(ts.header_fill, FillSpec)
        assert isinstance(ts.data_fill_odd, FillSpec)
        assert isinstance(ts.data_fill_even, FillSpec)

    def test_header_font_is_bold(self) -> None:
        ts = TableStyle()
        assert ts.header_font.bold is True

    def test_even_row_fill_different_from_odd(self) -> None:
        ts = TableStyle()
        assert ts.data_fill_odd.color != ts.data_fill_even.color

    def test_number_formats(self) -> None:
        ts = TableStyle()
        assert ts.number_format == "#,##0"
        assert ts.percent_format == "0.0%"
        assert ts.date_format == "yyyy-mm-dd"


class TestTitleStyle:
    """Tests for TitleStyle dataclass."""

    def test_default_is_large_bold(self) -> None:
        ts = TitleStyle()
        assert ts.font.size == 18
        assert ts.font.bold is True

    def test_left_aligned_by_default(self) -> None:
        ts = TitleStyle()
        assert ts.alignment == "left"


class TestSubtitleStyle:
    """Tests for SubtitleStyle dataclass."""

    def test_default_smaller_than_title(self) -> None:
        ss = SubtitleStyle()
        assert ss.font.size == 13
        assert ss.font.bold is False


class TestParagraphStyle:
    """Tests for ParagraphStyle dataclass."""

    def test_default_body_readable(self) -> None:
        ps = ParagraphStyle()
        assert ps.font.size == 10
        assert ps.alignment == "left"


class TestTheme:
    """Tests for the Theme container class."""

    def test_default_name_is_custom(self) -> None:
        t = Theme()
        assert t.name == "custom"

    def test_default_font_is_arial(self) -> None:
        t = Theme()
        assert t.global_font_name == "Arial"

    def test_chart_colors_are_10(self) -> None:
        t = Theme()
        assert len(t.chart_colors) == 10

    def test_all_chart_colors_returns_copy(self) -> None:
        t = Theme()
        colors = t.all_chart_colors
        colors.append("#XYZ")
        assert len(t.chart_colors) == 10  # original unchanged

    def test_sheet_margins(self) -> None:
        t = Theme()
        assert t.sheet_margin_rows == 2
        assert t.sheet_margin_cols == 1

    def test_element_spacing(self) -> None:
        t = Theme()
        assert t.element_spacing_rows == 2

    def test_border_constants(self) -> None:
        assert Theme.BORDER_THIN == 1
        assert Theme.BORDER_MEDIUM == 2
        assert Theme.BORDER_DASHED == 3
        assert Theme.BORDER_NONE == 0

    def test_repr_includes_name(self) -> None:
        t = Theme(name="my_theme")
        r = repr(t)
        assert "my_theme" in r

    def test_repr_includes_font(self) -> None:
        t = Theme(global_font_name="Calibri")
        r = repr(t)
        assert "Calibri" in r

    def test_custom_theme_override(self) -> None:
        t = Theme(
            name="custom_dark",
            global_font_name="Consolas",
            accent_color="#FF5500",
        )
        assert t.name == "custom_dark"
        assert t.global_font_name == "Consolas"
        assert t.accent_color == "#FF5500"
        # defaults should still be present
        assert isinstance(t.table, TableStyle)
        assert isinstance(t.title, TitleStyle)
