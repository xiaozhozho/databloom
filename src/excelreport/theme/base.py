"""Theme data classes for excelreport visual styling.

A Theme defines all visual properties needed to style a report:
- Fonts (family, sizes for different levels)
- Colors (table headers, alternating rows, borders)
- Chart color palettes
- Alignment and number format presets
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar


@dataclass
class FontSpec:
    """Font specification."""

    name: str = "Arial"
    size: int = 11
    bold: bool = False
    italic: bool = False
    color: str = "#000000"
    underline: bool = False


@dataclass
class FillSpec:
    """Cell fill / background specification."""

    color: str = "#FFFFFF"
    pattern: int = 1  # solid fill for xlsxwriter


@dataclass
class BorderSpec:
    """Cell border specification."""

    style: int = 1  # thin border
    color: str = "#D9D9D9"


@dataclass
class TableStyle:
    """Style for a data table."""

    header_font: FontSpec = field(default_factory=lambda: FontSpec(bold=True, size=11))
    header_fill: FillSpec = field(default_factory=lambda: FillSpec(color="#2F5496"))
    header_border: BorderSpec = field(default_factory=BorderSpec)
    data_font: FontSpec = field(default_factory=lambda: FontSpec(size=10))
    data_fill_odd: FillSpec = field(default_factory=lambda: FillSpec(color="#FFFFFF"))
    data_fill_even: FillSpec = field(default_factory=lambda: FillSpec(color="#F2F2F2"))
    data_border: BorderSpec = field(default_factory=BorderSpec)
    first_column_font: FontSpec = field(default_factory=lambda: FontSpec(size=10, bold=True))
    number_format: str = "#,##0"
    percent_format: str = "0.0%"
    date_format: str = "yyyy-mm-dd"
    currency_format: str = "#,##0.00"


@dataclass
class TitleStyle:
    """Style for title elements."""

    font: FontSpec = field(default_factory=lambda: FontSpec(size=18, bold=True, color="#1F3864"))
    alignment: str = "left"


@dataclass
class SubtitleStyle:
    """Style for subtitle elements."""

    font: FontSpec = field(default_factory=lambda: FontSpec(size=13, bold=False, color="#44546A"))
    alignment: str = "left"


@dataclass
class ParagraphStyle:
    """Style for paragraph / text body elements."""

    font: FontSpec = field(default_factory=lambda: FontSpec(size=10, color="#333333"))
    alignment: str = "left"


@dataclass
class Theme:
    """Complete visual theme for an Excel report.

    Contains all configurable style properties for tables, text elements,
    charts, and layout defaults. Use ``get_theme("business_blue")`` or
    instantiate directly with custom values.

    Attributes:
        name: Unique theme identifier.
        global_font_name: Default font family used unless overridden by
            element-specific styles.
        table: Table formatting (headers, alternating rows, borders,
            number formats).
        title: Main title text style.
        subtitle: Subtitle text style.
        paragraph: Body text style.
        chart_colors: List of hex colors used as series palette for charts.
        accent_color: Key accent hex color for highlights and KPI cards.
        sheet_margin_rows: Number of blank rows at the top of each sheet.
        sheet_margin_cols: Number of blank columns on the left.
        element_spacing_rows: Number of blank rows between elements.
    """

    name: str = "custom"
    global_font_name: str = "Arial"
    table: TableStyle = field(default_factory=TableStyle)
    title: TitleStyle = field(default_factory=TitleStyle)
    subtitle: SubtitleStyle = field(default_factory=SubtitleStyle)
    paragraph: ParagraphStyle = field(default_factory=ParagraphStyle)
    chart_colors: list[str] = field(
        default_factory=lambda: [
            "#2F5496",
            "#ED7D31",
            "#70AD47",
            "#FFC000",
            "#5B9BD5",
            "#A5A5A5",
            "#264478",
            "#BF8F00",
            "#4472C4",
            "#FF0000",
        ]
    )
    accent_color: str = "#2F5496"
    sheet_margin_rows: int = 2
    sheet_margin_cols: int = 1
    element_spacing_rows: int = 2

    # Predefined xlsxwriter border style constants for convenience.
    BORDER_THIN: ClassVar[int] = 1
    BORDER_MEDIUM: ClassVar[int] = 2
    BORDER_DASHED: ClassVar[int] = 3
    BORDER_DOTTED: ClassVar[int] = 4
    BORDER_NONE: ClassVar[int] = 0

    @property
    def all_chart_colors(self) -> list[str]:
        """Return chart colors as a list (mutable copy)."""
        return list(self.chart_colors)

    def __repr__(self) -> str:
        return f"Theme(name={self.name!r}, font={self.global_font_name!r})"
