"""Pre-built theme presets for databloom.

Ten carefully designed themes ready to use out of the box.
Import them directly or use ``get_theme(name)`` to retrieve by name.
"""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING

from databloom.theme.base import (
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
    "THEME_CLASSIC_WHITE",
    "THEME_CREATIVE_MAGENTA",
    "THEME_FINANCE_CHARCOAL",
    "THEME_FRESH_GREEN",
    "THEME_GOVERNMENT_NAVY",
    "THEME_MEDICAL_TEAL",
    "THEME_MINIMAL_GRAY",
    "THEME_TECH_DARK",
    "THEME_WARM_ORANGE",
    "THEME_SUNSET_CORAL",
    "THEME_OCEAN_DEPTHS",
    "THEME_FOREST_DAWN",
    "THEME_SLATE_PRO",
    "THEME_AMBER_ACADEMIC",
    "THEME_MIDNIGHT_PLUM",
    "THEME_SAGE_EARTH",
    "THEME_ARCTIC_FROST",
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
        "#548235",
        "#A9D18E",
        "#375623",
        "#70AD47",
        "#C5E0B4",
        "#ED7D31",
        "#5B9BD5",
        "#FFC000",
        "#BF8F00",
        "#264478",
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
        "#00BCD4",
        "#FF6E40",
        "#69F0AE",
        "#FFD740",
        "#40C4FF",
        "#B388FF",
        "#00B8D4",
        "#FF9100",
        "#448AFF",
        "#FF5252",
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
        "#ED7D31",
        "#70AD47",
        "#2F5496",
        "#FFC000",
        "#5B9BD5",
        "#BF8F00",
        "#A5A5A5",
        "#4472C4",
        "#548235",
        "#264478",
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
        "#555555",
        "#999999",
        "#777777",
        "#BBBBBB",
        "#333333",
        "#888888",
        "#666666",
        "#AAAAAA",
        "#444444",
        "#DDDDDD",
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
        "#000000",
        "#333333",
        "#666666",
        "#999999",
        "#CCCCCC",
        "#555555",
        "#777777",
        "#AAAAAA",
        "#444444",
        "#DDDDDD",
    ],
    accent_color="#000000",
)

# ── Finance Charcoal ──────────────────────────────────────────────────

THEME_FINANCE_CHARCOAL = Theme(
    name="finance_charcoal",
    global_font_name="Lato",
    table=TableStyle(
        header_font=FontSpec(name="Lato", size=11, bold=True, color="#FFFFFF"),
        header_fill=FillSpec(color="#374151"),
        header_border=BorderSpec(color="#374151"),
        data_font=FontSpec(name="Lato", size=10, color="#1F2937"),
        data_fill_odd=FillSpec(color="#FFFFFF"),
        data_fill_even=FillSpec(color="#F3F4F6"),
        data_border=BorderSpec(color="#D1D5DB"),
        number_format="#,##0",
        currency_format="#,##0.00",
    ),
    title=TitleStyle(
        font=FontSpec(name="Lato", size=20, bold=True, color="#1F2937"),
    ),
    subtitle=SubtitleStyle(
        font=FontSpec(name="Lato", size=13, color="#6B7280"),
    ),
    paragraph=ParagraphStyle(
        font=FontSpec(name="Lato", size=10, color="#374151"),
    ),
    chart_colors=[
        "#374151",
        "#DC2626",
        "#3B82F6",
        "#F59E0B",
        "#10B981",
        "#6B7280",
        "#1F2937",
        "#EF4444",
        "#2563EB",
        "#D97706",
    ],
    accent_color="#DC2626",
)

# ── Medical Teal ──────────────────────────────────────────────────────

THEME_MEDICAL_TEAL = Theme(
    name="medical_teal",
    global_font_name="Noto Sans",
    table=TableStyle(
        header_font=FontSpec(name="Noto Sans", size=11, bold=True, color="#FFFFFF"),
        header_fill=FillSpec(color="#0D9488"),
        header_border=BorderSpec(color="#0D9488"),
        data_font=FontSpec(name="Noto Sans", size=10, color="#134E4A"),
        data_fill_odd=FillSpec(color="#FFFFFF"),
        data_fill_even=FillSpec(color="#F0FDFA"),
        data_border=BorderSpec(color="#99F6E4"),
    ),
    title=TitleStyle(
        font=FontSpec(name="Noto Sans", size=20, bold=True, color="#115E59"),
    ),
    subtitle=SubtitleStyle(
        font=FontSpec(name="Noto Sans", size=13, color="#14B8A6"),
    ),
    paragraph=ParagraphStyle(
        font=FontSpec(name="Noto Sans", size=10, color="#134E4A"),
    ),
    chart_colors=[
        "#0D9488",
        "#06B6D4",
        "#84CC16",
        "#F97316",
        "#6366F1",
        "#EC4899",
        "#14B8A6",
        "#3B82F6",
        "#22C55E",
        "#EAB308",
    ],
    accent_color="#0891B2",
)

# ── Creative Magenta ──────────────────────────────────────────────────

THEME_CREATIVE_MAGENTA = Theme(
    name="creative_magenta",
    global_font_name="Poppins",
    table=TableStyle(
        header_font=FontSpec(name="Poppins", size=11, bold=True, color="#FFFFFF"),
        header_fill=FillSpec(color="#BE185D"),
        header_border=BorderSpec(color="#BE185D"),
        data_font=FontSpec(name="Poppins", size=10, color="#500724"),
        data_fill_odd=FillSpec(color="#FFFFFF"),
        data_fill_even=FillSpec(color="#FDF2F8"),
        data_border=BorderSpec(color="#FBCFE8"),
    ),
    title=TitleStyle(
        font=FontSpec(name="Poppins", size=20, bold=True, color="#831843"),
    ),
    subtitle=SubtitleStyle(
        font=FontSpec(name="Poppins", size=13, color="#DB2777"),
    ),
    paragraph=ParagraphStyle(
        font=FontSpec(name="Poppins", size=10, color="#701A75"),
    ),
    chart_colors=[
        "#BE185D",
        "#7C3AED",
        "#06B6D4",
        "#F59E0B",
        "#10B981",
        "#EF4444",
        "#EC4899",
        "#3B82F6",
        "#F97316",
        "#84CC16",
    ],
    accent_color="#F43F5E",
)

# ── Government Navy ───────────────────────────────────────────────────

THEME_GOVERNMENT_NAVY = Theme(
    name="government_navy",
    global_font_name="Source Sans 3",
    table=TableStyle(
        header_font=FontSpec(name="Source Sans 3", size=11, bold=True, color="#FFFFFF"),
        header_fill=FillSpec(color="#1E3A5F"),
        header_border=BorderSpec(color="#1E3A5F"),
        data_font=FontSpec(name="Source Sans 3", size=10, color="#0F172A"),
        data_fill_odd=FillSpec(color="#FFFFFF"),
        data_fill_even=FillSpec(color="#F8FAFC"),
        data_border=BorderSpec(color="#CBD5E1"),
    ),
    title=TitleStyle(
        font=FontSpec(name="Source Sans 3", size=20, bold=True, color="#0F172A"),
    ),
    subtitle=SubtitleStyle(
        font=FontSpec(name="Source Sans 3", size=13, color="#475569"),
    ),
    paragraph=ParagraphStyle(
        font=FontSpec(name="Source Sans 3", size=10, color="#1E293B"),
    ),
    chart_colors=[
        "#1E3A5F",
        "#B45309",
        "#0F766E",
        "#6D28D9",
        "#0369A1",
        "#15803D",
        "#0F172A",
        "#D97706",
        "#475569",
        "#BE123C",
    ],
    accent_color="#B45309",
)

# ── Sunset Coral ───────────────────────────────────────────────────

THEME_SUNSET_CORAL = Theme(
    name="sunset_coral",
    global_font_name="Nunito",
    table=TableStyle(
        header_font=FontSpec(name="Nunito", size=11, bold=True, color="#FFFFFF"),
        header_fill=FillSpec(color="#E07A5F"),
        header_border=BorderSpec(color="#E07A5F"),
        data_font=FontSpec(name="Nunito", size=10, color="#3D2C2E"),
        data_fill_odd=FillSpec(color="#FFFFFF"),
        data_fill_even=FillSpec(color="#FDF0ED"),
        data_border=BorderSpec(color="#F4C6B7"),
    ),
    title=TitleStyle(
        font=FontSpec(name="Nunito", size=20, bold=True, color="#C35A3F"),
    ),
    subtitle=SubtitleStyle(
        font=FontSpec(name="Nunito", size=13, color="#E07A5F"),
    ),
    paragraph=ParagraphStyle(
        font=FontSpec(name="Nunito", size=10, color="#5C3D33"),
    ),
    chart_colors=[
        "#E07A5F", "#F2CC8F", "#81B29A", "#7B5EA7",
        "#F4A261", "#E9C46A", "#3D405B", "#2A9D8F",
        "#E76F51", "#264653",
    ],
    accent_color="#E07A5F",
)

# ── Ocean Depths ────────────────────────────────────────────────────

THEME_OCEAN_DEPTHS = Theme(
    name="ocean_depths",
    global_font_name="Roboto",
    table=TableStyle(
        header_font=FontSpec(name="Roboto", size=11, bold=True, color="#FFFFFF"),
        header_fill=FillSpec(color="#006D77"),
        header_border=BorderSpec(color="#006D77"),
        data_font=FontSpec(name="Roboto", size=10, color="#1B3A4B"),
        data_fill_odd=FillSpec(color="#FFFFFF"),
        data_fill_even=FillSpec(color="#E8F4F8"),
        data_border=BorderSpec(color="#B8D8E3"),
    ),
    title=TitleStyle(
        font=FontSpec(name="Roboto", size=20, bold=True, color="#004E5C"),
    ),
    subtitle=SubtitleStyle(
        font=FontSpec(name="Roboto", size=13, color="#007790"),
    ),
    paragraph=ParagraphStyle(
        font=FontSpec(name="Roboto", size=10, color="#2C5F6E"),
    ),
    chart_colors=[
        "#006D77", "#83C5BE", "#003D4D", "#00A8B5",
        "#FFD166", "#EF476F", "#EDAE49", "#118AB2",
        "#073B4C", "#06D6A0",
    ],
    accent_color="#006D77",
)

# ── Forest Dawn ─────────────────────────────────────────────────────

THEME_FOREST_DAWN = Theme(
    name="forest_dawn",
    global_font_name="Lora",
    table=TableStyle(
        header_font=FontSpec(name="Lora", size=11, bold=True, color="#FFFFFF"),
        header_fill=FillSpec(color="#5E503F"),
        header_border=BorderSpec(color="#5E503F"),
        data_font=FontSpec(name="Lora", size=10, color="#3B3024"),
        data_fill_odd=FillSpec(color="#FFFFFF"),
        data_fill_even=FillSpec(color="#F5F0E8"),
        data_border=BorderSpec(color="#D4C9B5"),
    ),
    title=TitleStyle(
        font=FontSpec(name="Lora", size=20, bold=True, color="#4A3F2E"),
    ),
    subtitle=SubtitleStyle(
        font=FontSpec(name="Lora", size=13, color="#8B7355"),
    ),
    paragraph=ParagraphStyle(
        font=FontSpec(name="Lora", size=10, color="#5C4A33"),
    ),
    chart_colors=[
        "#5E503F", "#A7C957", "#6A994E", "#C08552",
        "#DD9787", "#DDA15E", "#386641", "#BC6C25",
        "#606C38", "#283618",
    ],
    accent_color="#5E503F",
)

# ── Slate Pro ───────────────────────────────────────────────────────

THEME_SLATE_PRO = Theme(
    name="slate_pro",
    global_font_name="IBM Plex Sans",
    table=TableStyle(
        header_font=FontSpec(name="IBM Plex Sans", size=11, bold=True, color="#FFFFFF"),
        header_fill=FillSpec(color="#4A5568"),
        header_border=BorderSpec(color="#4A5568"),
        data_font=FontSpec(name="IBM Plex Sans", size=10, color="#1A202C"),
        data_fill_odd=FillSpec(color="#FFFFFF"),
        data_fill_even=FillSpec(color="#F7FAFC"),
        data_border=BorderSpec(color="#CBD5E0"),
        number_format="#,##0",
        currency_format="#,##0.00",
    ),
    title=TitleStyle(
        font=FontSpec(name="IBM Plex Sans", size=20, bold=True, color="#2D3748"),
    ),
    subtitle=SubtitleStyle(
        font=FontSpec(name="IBM Plex Sans", size=13, color="#718096"),
    ),
    paragraph=ParagraphStyle(
        font=FontSpec(name="IBM Plex Sans", size=10, color="#4A5568"),
    ),
    chart_colors=[
        "#4A5568", "#68D391", "#4299E1", "#F6AD55",
        "#FC8181", "#B794F4", "#2D3748", "#48BB78",
        "#3182CE", "#ED8936",
    ],
    accent_color="#4A5568",
)

# ── Amber Academic ──────────────────────────────────────────────────

THEME_AMBER_ACADEMIC = Theme(
    name="amber_academic",
    global_font_name="Georgia",
    table=TableStyle(
        header_font=FontSpec(name="Georgia", size=11, bold=True, color="#FFFFFF"),
        header_fill=FillSpec(color="#A0522D"),
        header_border=BorderSpec(color="#A0522D"),
        data_font=FontSpec(name="Georgia", size=10, color="#3E2723"),
        data_fill_odd=FillSpec(color="#FFFFFF"),
        data_fill_even=FillSpec(color="#FFF8E7"),
        data_border=BorderSpec(color="#E0C9A6"),
        number_format="#,##0",
        currency_format="#,##0.00",
    ),
    title=TitleStyle(
        font=FontSpec(name="Georgia", size=20, bold=True, color="#8B4513"),
    ),
    subtitle=SubtitleStyle(
        font=FontSpec(name="Georgia", size=13, color="#CD853F"),
    ),
    paragraph=ParagraphStyle(
        font=FontSpec(name="Georgia", size=10, color="#5D4037"),
    ),
    chart_colors=[
        "#A0522D", "#D4A76A", "#78909C", "#66BB6A",
        "#D4A76A", "#8D6E63", "#FFA726", "#5C6BC0",
        "#EF5350", "#26A69A",
    ],
    accent_color="#A0522D",
)

# ── Midnight Plum ───────────────────────────────────────────────────

THEME_MIDNIGHT_PLUM = Theme(
    name="midnight_plum",
    global_font_name="Montserrat",
    table=TableStyle(
        header_font=FontSpec(name="Montserrat", size=11, bold=True, color="#FFFFFF"),
        header_fill=FillSpec(color="#4A235A"),
        header_border=BorderSpec(color="#4A235A"),
        data_font=FontSpec(name="Montserrat", size=10, color="#2D1133"),
        data_fill_odd=FillSpec(color="#FFFFFF"),
        data_fill_even=FillSpec(color="#F8F0FA"),
        data_border=BorderSpec(color="#D7BDE2"),
    ),
    title=TitleStyle(
        font=FontSpec(name="Montserrat", size=20, bold=True, color="#3D1A4F"),
    ),
    subtitle=SubtitleStyle(
        font=FontSpec(name="Montserrat", size=13, color="#7D3C98"),
    ),
    paragraph=ParagraphStyle(
        font=FontSpec(name="Montserrat", size=10, color="#4A235A"),
    ),
    chart_colors=[
        "#4A235A", "#C39BD3", "#8E44AD", "#F1C40F",
        "#E67E22", "#1ABC9C", "#2C3E50", "#E74C3C",
        "#7D3C98", "#3498DB",
    ],
    accent_color="#7D3C98",
)

# ── Sage Earth ──────────────────────────────────────────────────────

THEME_SAGE_EARTH = Theme(
    name="sage_earth",
    global_font_name="Work Sans",
    table=TableStyle(
        header_font=FontSpec(name="Work Sans", size=11, bold=True, color="#FFFFFF"),
        header_fill=FillSpec(color="#6B705C"),
        header_border=BorderSpec(color="#6B705C"),
        data_font=FontSpec(name="Work Sans", size=10, color="#3E3D31"),
        data_fill_odd=FillSpec(color="#FFFFFF"),
        data_fill_even=FillSpec(color="#F5F3EE"),
        data_border=BorderSpec(color="#CECBBC"),
    ),
    title=TitleStyle(
        font=FontSpec(name="Work Sans", size=20, bold=True, color="#4A4E3F"),
    ),
    subtitle=SubtitleStyle(
        font=FontSpec(name="Work Sans", size=13, color="#8A8D7A"),
    ),
    paragraph=ParagraphStyle(
        font=FontSpec(name="Work Sans", size=10, color="#5B5C4E"),
    ),
    chart_colors=[
        "#6B705C", "#DDB892", "#A5A58D", "#B7B7A4",
        "#EFC3A4", "#956C5B", "#937B63", "#C4A882",
        "#7B8F6A", "#5D6B4C",
    ],
    accent_color="#6B705C",
)

# ── Arctic Frost ────────────────────────────────────────────────────

THEME_ARCTIC_FROST = Theme(
    name="arctic_frost",
    global_font_name="Inter",
    table=TableStyle(
        header_font=FontSpec(name="Inter", size=11, bold=True, color="#1B2838"),
        header_fill=FillSpec(color="#B8D4E3"),
        header_border=BorderSpec(color="#B8D4E3"),
        data_font=FontSpec(name="Inter", size=10, color="#1B2838"),
        data_fill_odd=FillSpec(color="#FFFFFF"),
        data_fill_even=FillSpec(color="#EDF4F8"),
        data_border=BorderSpec(color="#D6E6F0"),
    ),
    title=TitleStyle(
        font=FontSpec(name="Inter", size=20, bold=True, color="#0F3B5C"),
    ),
    subtitle=SubtitleStyle(
        font=FontSpec(name="Inter", size=13, color="#5B8FA8"),
    ),
    paragraph=ParagraphStyle(
        font=FontSpec(name="Inter", size=10, color="#2C4B60"),
    ),
    chart_colors=[
        "#318FB5", "#6EC4DB", "#8CDFF0", "#1B5E7B",
        "#F4976C", "#B8D4E3", "#A8DADC", "#457B9D",
        "#E63946", "#1D3557",
    ],
    accent_color="#318FB5",
)

# ── Theme registry ──────────────────────────────────────────────────

_THEME_REGISTRY: dict[str, Theme] = {
    "business_blue": THEME_BUSINESS_BLUE,
    "fresh_green": THEME_FRESH_GREEN,
    "tech_dark": THEME_TECH_DARK,
    "warm_orange": THEME_WARM_ORANGE,
    "minimal_gray": THEME_MINIMAL_GRAY,
    "classic_white": THEME_CLASSIC_WHITE,
    "finance_charcoal": THEME_FINANCE_CHARCOAL,
    "medical_teal": THEME_MEDICAL_TEAL,
    "creative_magenta": THEME_CREATIVE_MAGENTA,
    "government_navy": THEME_GOVERNMENT_NAVY,
    "sunset_coral": THEME_SUNSET_CORAL,
    "ocean_depths": THEME_OCEAN_DEPTHS,
    "forest_dawn": THEME_FOREST_DAWN,
    "slate_pro": THEME_SLATE_PRO,
    "amber_academic": THEME_AMBER_ACADEMIC,
    "midnight_plum": THEME_MIDNIGHT_PLUM,
    "sage_earth": THEME_SAGE_EARTH,
    "arctic_frost": THEME_ARCTIC_FROST,
}


def get_theme(name: str) -> Theme:
    """Retrieve a deep copy of a built-in theme by name.

    Args:
        name: Theme name, e.g. ``"business_blue"``.

    Returns:
        A deep copy of the matching ``Theme`` instance — safe to mutate
        without affecting the global preset.

    Raises:
        KeyError: If the theme name is not found.
    """
    if name not in _THEME_REGISTRY:
        available = ", ".join(_THEME_REGISTRY)
        raise KeyError(f"Theme {name!r} not found. Available: {available}")
    return copy.deepcopy(_THEME_REGISTRY[name])


def list_themes() -> list[str]:
    """Return the names of all available built-in themes."""
    return sorted(_THEME_REGISTRY)
