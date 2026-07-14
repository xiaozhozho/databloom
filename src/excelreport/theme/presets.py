"""Preset themes — not yet implemented."""

from excelreport.theme.base import Theme

THEME_BUSINESS_BLUE = Theme()
THEME_FRESH_GREEN = Theme()
THEME_TECH_DARK = Theme()
THEME_WARM_ORANGE = Theme()
THEME_MINIMAL_GRAY = Theme()
THEME_CLASSIC_WHITE = Theme()


def get_theme(name: str) -> Theme:
    """Placeholder."""
    return Theme()


def list_themes() -> list[str]:
    """Placeholder."""
    return []
