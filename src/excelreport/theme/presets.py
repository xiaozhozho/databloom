"""Pre-built theme presets for excelreport.

Six carefully designed themes ready to use out of the box.
Import them directly or use ``get_theme(name)`` to retrieve by name.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

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

if TYPE_CHECKING:
    pass

__all__ = [
    "THEME_BUSINESS_BLUE",
    "THEME_FRESH_GREEN",
    "THEME_TECH_DARK",
    "THEME_WARM_ORANGE",
    "THEME_MINIMAL_GRAY",
    "THEME_CLASSIC_WHITE",
    "get_theme",
    "list_themes",
]

# ── Business Blue ───────────────────────────────────────────────────

THEME_BUSINESS_BLUE = Theme(
    name="business_blue",
    global_font_name="Arial",
    table=TableStyle(
        header_font=FontSpec(name="Arial", size=11, bold=True, color="#FFFFFF"),
        header_fill=FillSpec(color="#2F5496"),
        header_border=BorderSpec(color="#2F5496"),
        data_font=FontSpec(name="Arial", size=10, color="#333333"),
        data_fill_odd=FillSpec(color="#FFFFFF"),
        data_fill_even=FillSpec(color="#F2F7FC"),
        data_border=BorderSpec(color="#D6E4F0"),
    ),
    title=TitleStyle(
        font=FontSpec(name="Arial", size=20, bold=True, color="#1F3864"),
    ),
    subtitle=SubtitleStyle(
        font=FontSpec(name="Arial", size=13, color="#5B7EB5"),
    ),
    paragraph=ParagraphStyle(
        font=FontSpec(name="Arial", size=10, color="#444444"),
    ),
    chart_colors=[
        "#2F5496", "#ED7D31", "#70AD47", "#FFC000", "#5B9BD5",
        "#A5A5A5", "#264478", "#BF8F00", "#4472C4", "#FF0000",
    ],
    accent_color="#2F5496",
)

# ── Fresh Green ─────────────────────────────────────────────────────

THEME_FRESH_GREEN = Theme(
    name="fresh_green",
    global_font_name="Calibri",
    table=TableStyle(
        header_font=FontSpec(name="Calibri", size=11, bold=True, color="#FFFFFF"),
        header_fill=FillSpec(color="#548235"),
        header_border=BorderSpec(color="#548235"),
        data_font=FontSpec(name="Calibri", size=10, color="#2D3B20"),
        data_fill_odd=FillSpec(color="#FFFFFF"),
        data_fill_even=FillSpec(color="#EDF6E8"),
        data_border=BorderSpec(color="#C5E0B4"),
        number_format="#,##0",
        currency_format="#,##0.00",
    ),
    title=TitleStyle(
        font=FontSpec(name="Calibri", size=20, bold=True, color="#375623"),
    ),
    subtitle=SubtitleStyle(
        font=FontSpec(name="Calibri", size=13, color="#70AD47"),
    ),
    paragraph=ParagraphStyle(
        font=FontSpec(name="Calibri", size=10, color="#4A5A3B"),
    ),
    chart_colors=[
        "#548235", "#A9D18E", "#375623", "#70AD47", "#C5E0B4",
        "#ED7D31", "#5B9BD5", "#FFC000", "#BF8F00", "#264478",
    ],
    accent_color="#548235",
)

# ── Tech Dark ───────────────────────────────────────────────────────

THEME_TECH_DARK = Theme(
    name="tech_dark",
    global_font_name="Segoe UI",
    table=TableStyle(
        header_font=FontSpec(name="Segoe UI", size=11, bold=True, color="#2D2D2D"),
        header_fill=FillSpec(color="#00BCD4"),
        header_border=BorderSpec(color="#00BCD4"),
        data_font=FontSpec(name="Segoe UI", size=10, color="#E0E0E0"),
        data_fill_odd=FillSpec(color="#333333"),
        data_fill_even=FillSpec(color="#2A2A2A"),
        data_border=BorderSpec(color="#444444"),
    ),
    title=TitleStyle(
        font=FontSpec(name="Segoe UI", size=20, bold=True, color="#00BCD4"),
    ),
    subtitle=SubtitleStyle(
        font=FontSpec(name="Segoe UI", size=13, color="#80DEE4"),
    ),
    paragraph=ParagraphStyle(
        font=FontSpec(name="Segoe UI", size=10, color="#BDBDBD"),
    ),
    chart_colors=[
        "#00BCD4", "#FF6E40", "#69F0AE", "#FFD740", "#40C4FF",
        "#B388FF", "#00B8D4", "#FF9100", "#448AFF", "#FF5252",
    ],
    accent_color="#00BCD4",
)

# ── Warm Orange ─────────────────────────────────────────────────────

THEME_WARM_ORANGE = Theme(
    name="warm_orange",
    global_font_name="Tahoma",
    table=TableStyle(
        header_font=FontSpec(name="Tahoma", size=11, bold=True, color="#FFFFFF"),
        header_fill=FillSpec(color="#ED7D31"),
        header_border=BorderSpec(color="#ED7D31"),
        data_font=FontSpec(name="Tahoma", size=10, color="#4A2800"),
        data_fill_odd=FillSpec(color="#FFFFFF"),
        data_fill_even=FillSpec(color="#FFF3E6"),
        data_border=BorderSpec(color="#F5CDAA"),
    ),
    title=TitleStyle(
        font=FontSpec(name="Tahoma", size=20, bold=True, color="#C55A11"),
    ),
    subtitle=SubtitleStyle(
        font=FontSpec(name="Tahoma", size=13, color="#ED7D31"),
    ),
    paragraph=ParagraphStyle(
        font=FontSpec(name="Tahoma", size=10, color="#5C3A1E"),
    ),
    chart_colors=[
        "#ED7D31", "#70AD47", "#2F5496", "#FFC000", "#5B9BD5",
        "#BF8F00", "#A5A5A5", "#4472C4", "#548235", "#264478",
    ],
    accent_color="#ED7D31",
)

# ── Minimal Gray ────────────────────────────────────────────────────

THEME_MINIMAL_GRAY = Theme(
    name="minimal_gray",
    global_font_name="Helvetica",
    table=TableStyle(
        header_font=FontSpec(name="Helvetica", size=11, bold=True, color="#333333"),
        header_fill=FillSpec(color="#E0E0E0"),
        header_border=BorderSpec(color="#CCCCCC"),
        data_font=FontSpec(name="Helvetica", size=10, color="#333333"),
        data_fill_odd=FillSpec(color="#FFFFFF"),
        data_fill_even=FillSpec(color="#FAFAFA"),
        data_border=BorderSpec(color="#E0E0E0"),
    ),
    title=TitleStyle(
        font=FontSpec(name="Helvetica", size=20, bold=True, color="#333333"),
    ),
    subtitle=SubtitleStyle(
        font=FontSpec(name="Helvetica", size=13, color="#777777"),
    ),
    paragraph=ParagraphStyle(
        font=FontSpec(name="Helvetica", size=10, color="#555555"),
    ),
    chart_colors=[
        "#555555", "#999999", "#777777", "#BBBBBB", "#333333",
        "#888888", "#666666", "#AAAAAA", "#444444", "#DDDDDD",
    ],
    accent_color="#555555",
)

# ── Classic White ───────────────────────────────────────────────────

THEME_CLASSIC_WHITE = Theme(
    name="classic_white",
    global_font_name="Arial",
    table=TableStyle(
        header_font=FontSpec(name="Arial", size=11, bold=True, color="#000000"),
        header_fill=FillSpec(color="#FFFFFF"),
        header_border=BorderSpec(color="#999999"),
        data_font=FontSpec(name="Arial", size=10, color="#000000"),
        data_fill_odd=FillSpec(color="#FFFFFF"),
        data_fill_even=FillSpec(color="#FFFFFF"),
        data_border=BorderSpec(color="#CCCCCC"),
    ),
    title=TitleStyle(
        font=FontSpec(name="Arial", size=18, bold=True, color="#000000"),
    ),
    subtitle=SubtitleStyle(
        font=FontSpec(name="Arial", size=12, color="#444444"),
    ),
    paragraph=ParagraphStyle(
        font=FontSpec(name="Arial", size=10, color="#000000"),
    ),
    chart_colors=[
        "#000000", "#333333", "#666666", "#999999", "#CCCCCC",
        "#555555", "#777777", "#AAAAAA", "#444444", "#DDDDDD",
    ],
    accent_color="#000000",
)

# ── Theme registry ──────────────────────────────────────────────────

_THEME_REGISTRY: dict[str, Theme] = {
    "business_blue": THEME_BUSINESS_BLUE,
    "fresh_green": THEME_FRESH_GREEN,
    "tech_dark": THEME_TECH_DARK,
    "warm_orange": THEME_WARM_ORANGE,
    "minimal_gray": THEME_MINIMAL_GRAY,
    "classic_white": THEME_CLASSIC_WHITE,
}


def get_theme(name: str) -> Theme:
    """Retrieve a built-in theme by name.

    Args:
        name: Theme name, e.g. ``"business_blue"``.

    Returns:
        A copy of the matching ``Theme`` instance.

    Raises:
        KeyError: If the theme name is not found.
    """
    if name not in _THEME_REGISTRY:
        available = ", ".join(_THEME_REGISTRY)
        raise KeyError(
            f"Theme {name!r} not found. Available: {available}"
        )
    return _THEME_REGISTRY[name]


def list_themes() -> list[str]:
    """Return the names of all available built-in themes."""
    return sorted(_THEME_REGISTRY)
