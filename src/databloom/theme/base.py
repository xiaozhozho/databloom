"""Theme data classes for databloom visual styling.

A Theme defines all visual properties needed to style a report:
- Fonts (family, sizes for different levels)
- Colors (table headers, alternating rows, borders)
- Chart color palettes
- Alignment and number format presets
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar

from databloom.settings import settings


@dataclass
class FontSpec:
    """Font specification."""

    name: str = field(default_factory=lambda: settings.theme_defaults.font_name)
    size: int = field(default_factory=lambda: settings.theme_defaults.font_size)
    bold: bool = field(default_factory=lambda: settings.theme_defaults.font_bold)
    italic: bool = field(default_factory=lambda: settings.theme_defaults.font_italic)
    color: str = field(default_factory=lambda: settings.theme_defaults.font_color)
    underline: bool = field(default_factory=lambda: settings.theme_defaults.font_underline)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "size": self.size,
            "bold": self.bold,
            "italic": self.italic,
            "color": self.color,
            "underline": self.underline,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> FontSpec:
        return cls(
            name=d.get("name", "Arial"),
            size=d.get("size", 11),
            bold=d.get("bold", False),
            italic=d.get("italic", False),
            color=d.get("color", "#000000"),
            underline=d.get("underline", False),
        )


@dataclass
class FillSpec:
    """Cell fill / background specification."""

    color: str = field(default_factory=lambda: settings.theme_defaults.fill_color)
    pattern: int = field(default_factory=lambda: settings.theme_defaults.fill_pattern)  # solid fill for xlsxwriter

    def to_dict(self) -> dict[str, Any]:
        return {"color": self.color, "pattern": self.pattern}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> FillSpec:
        return cls(color=d.get("color", "#FFFFFF"), pattern=d.get("pattern", 1))


@dataclass
class BorderSpec:
    """Cell border specification."""

    style: int = field(default_factory=lambda: settings.theme_defaults.border_style)  # thin border
    color: str = field(default_factory=lambda: settings.theme_defaults.border_color)

    def to_dict(self) -> dict[str, Any]:
        return {"style": self.style, "color": self.color}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> BorderSpec:
        return cls(style=d.get("style", 1), color=d.get("color", "#D9D9D9"))


@dataclass
class TableStyle:
    """Style for a data table."""

    header_font: FontSpec = field(
        default_factory=lambda: FontSpec(
            bold=True, size=settings.theme_defaults.table_header_font_size
        )
    )
    header_fill: FillSpec = field(
        default_factory=lambda: FillSpec(color=settings.theme_defaults.table_header_fill_color)
    )
    header_border: BorderSpec = field(default_factory=BorderSpec)
    data_font: FontSpec = field(
        default_factory=lambda: FontSpec(size=settings.theme_defaults.table_data_font_size)
    )
    data_fill_odd: FillSpec = field(
        default_factory=lambda: FillSpec(color=settings.theme_defaults.table_data_fill_odd_color)
    )
    data_fill_even: FillSpec = field(
        default_factory=lambda: FillSpec(color=settings.theme_defaults.table_data_fill_even_color)
    )
    data_border: BorderSpec = field(default_factory=BorderSpec)
    first_column_font: FontSpec = field(
        default_factory=lambda: FontSpec(
            size=settings.theme_defaults.table_first_column_font_size, bold=True
        )
    )
    number_format: str = field(
        default_factory=lambda: settings.theme_defaults.table_number_format
    )
    percent_format: str = field(
        default_factory=lambda: settings.theme_defaults.table_percent_format
    )
    date_format: str = field(
        default_factory=lambda: settings.theme_defaults.table_date_format
    )
    currency_format: str = field(
        default_factory=lambda: settings.theme_defaults.table_currency_format
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "header_font": self.header_font.to_dict(),
            "header_fill": self.header_fill.to_dict(),
            "header_border": self.header_border.to_dict(),
            "data_font": self.data_font.to_dict(),
            "data_fill_odd": self.data_fill_odd.to_dict(),
            "data_fill_even": self.data_fill_even.to_dict(),
            "data_border": self.data_border.to_dict(),
            "first_column_font": self.first_column_font.to_dict(),
            "number_format": self.number_format,
            "percent_format": self.percent_format,
            "date_format": self.date_format,
            "currency_format": self.currency_format,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TableStyle:
        return cls(
            header_font=FontSpec.from_dict(d.get("header_font", {})),
            header_fill=FillSpec.from_dict(d.get("header_fill", {})),
            header_border=BorderSpec.from_dict(d.get("header_border", {})),
            data_font=FontSpec.from_dict(d.get("data_font", {})),
            data_fill_odd=FillSpec.from_dict(d.get("data_fill_odd", {})),
            data_fill_even=FillSpec.from_dict(d.get("data_fill_even", {})),
            data_border=BorderSpec.from_dict(d.get("data_border", {})),
            first_column_font=FontSpec.from_dict(d.get("first_column_font", {})),
            number_format=d.get("number_format", "#,##0"),
            percent_format=d.get("percent_format", "0.0%"),
            date_format=d.get("date_format", "yyyy-mm-dd"),
            currency_format=d.get("currency_format", "#,##0.00"),
        )


@dataclass
class TitleStyle:
    """Style for title elements."""

    font: FontSpec = field(
        default_factory=lambda: FontSpec(
            size=settings.theme_defaults.title_font_size,
            bold=True,
            color=settings.theme_defaults.title_font_color,
        )
    )
    alignment: str = field(default_factory=lambda: settings.theme_defaults.title_alignment)

    def to_dict(self) -> dict[str, Any]:
        return {"font": self.font.to_dict(), "alignment": self.alignment}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TitleStyle:
        return cls(font=FontSpec.from_dict(d.get("font", {})), alignment=d.get("alignment", "left"))


@dataclass
class SubtitleStyle:
    """Style for subtitle elements."""

    font: FontSpec = field(
        default_factory=lambda: FontSpec(
            size=settings.theme_defaults.subtitle_font_size,
            bold=False,
            color=settings.theme_defaults.subtitle_font_color,
        )
    )
    alignment: str = field(default_factory=lambda: settings.theme_defaults.subtitle_alignment)

    def to_dict(self) -> dict[str, Any]:
        return {"font": self.font.to_dict(), "alignment": self.alignment}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> SubtitleStyle:
        return cls(font=FontSpec.from_dict(d.get("font", {})), alignment=d.get("alignment", "left"))


@dataclass
class ParagraphStyle:
    """Style for paragraph / text body elements."""

    font: FontSpec = field(
        default_factory=lambda: FontSpec(
            size=settings.theme_defaults.paragraph_font_size,
            color=settings.theme_defaults.paragraph_font_color,
        )
    )
    alignment: str = field(default_factory=lambda: settings.theme_defaults.paragraph_alignment)

    def to_dict(self) -> dict[str, Any]:
        return {"font": self.font.to_dict(), "alignment": self.alignment}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ParagraphStyle:
        return cls(font=FontSpec.from_dict(d.get("font", {})), alignment=d.get("alignment", "left"))


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

    name: str = field(default_factory=lambda: settings.theme_defaults.name)
    global_font_name: str = field(default_factory=lambda: settings.theme_defaults.global_font_name)
    table: TableStyle = field(default_factory=TableStyle)
    title: TitleStyle = field(default_factory=TitleStyle)
    subtitle: SubtitleStyle = field(default_factory=SubtitleStyle)
    paragraph: ParagraphStyle = field(default_factory=ParagraphStyle)
    chart_colors: list[str] = field(
        default_factory=lambda: list(settings.theme_defaults.chart_colors)
    )
    accent_color: str = field(default_factory=lambda: settings.theme_defaults.accent_color)
    sheet_margin_rows: int = field(
        default_factory=lambda: settings.theme_defaults.sheet_margin_rows
    )
    sheet_margin_cols: int = field(
        default_factory=lambda: settings.theme_defaults.sheet_margin_cols
    )
    element_spacing_rows: int = field(
        default_factory=lambda: settings.theme_defaults.element_spacing_rows
    )

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

    def to_dict(self) -> dict[str, Any]:
        """Serialize this theme to a dictionary.

        Useful for storing themes as JSON/YAML for team sharing,
        version control, or dynamic configuration.

        Returns:
            A nested dict representation of the full theme.
        """
        return {
            "name": self.name,
            "global_font_name": self.global_font_name,
            "table": self.table.to_dict(),
            "title": self.title.to_dict(),
            "subtitle": self.subtitle.to_dict(),
            "paragraph": self.paragraph.to_dict(),
            "chart_colors": self.chart_colors,
            "accent_color": self.accent_color,
            "sheet_margin_rows": self.sheet_margin_rows,
            "sheet_margin_cols": self.sheet_margin_cols,
            "element_spacing_rows": self.element_spacing_rows,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Theme:
        """Deserialize a theme from a dictionary.

        Args:
            d: A dict previously produced by ``to_dict()``,
                or manually crafted with the same structure.

        Returns:
            A new ``Theme`` instance.
        """
        return cls(
            name=d.get("name", "custom"),
            global_font_name=d.get("global_font_name", "Arial"),
            table=TableStyle.from_dict(d.get("table", {})),
            title=TitleStyle.from_dict(d.get("title", {})),
            subtitle=SubtitleStyle.from_dict(d.get("subtitle", {})),
            paragraph=ParagraphStyle.from_dict(d.get("paragraph", {})),
            chart_colors=d.get("chart_colors", ["#2F5496"]),
            accent_color=d.get("accent_color", "#2F5496"),
            sheet_margin_rows=d.get("sheet_margin_rows", 2),
            sheet_margin_cols=d.get("sheet_margin_cols", 1),
            element_spacing_rows=d.get("element_spacing_rows", 2),
        )

    def __repr__(self) -> str:
        return f"Theme(name={self.name!r}, font={self.global_font_name!r})"
