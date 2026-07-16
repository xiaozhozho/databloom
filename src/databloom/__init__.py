"""databloom — Beautiful Excel reports from pandas DataFrames."""

from databloom.facade.quick import quick_report
from databloom.facade.report import Report
from databloom.theme.base import Theme
from databloom.theme.presets import (
    THEME_AMBER_ACADEMIC,
    THEME_ARCTIC_FROST,
    THEME_BUSINESS_BLUE,
    THEME_CLASSIC_WHITE,
    THEME_CREATIVE_MAGENTA,
    THEME_FINANCE_CHARCOAL,
    THEME_FOREST_DAWN,
    THEME_FRESH_GREEN,
    THEME_GOVERNMENT_NAVY,
    THEME_MEDICAL_TEAL,
    THEME_MIDNIGHT_PLUM,
    THEME_MINIMAL_GRAY,
    THEME_OCEAN_DEPTHS,
    THEME_SAGE_EARTH,
    THEME_SLATE_PRO,
    THEME_SUNSET_CORAL,
    THEME_TECH_DARK,
    THEME_WARM_ORANGE,
    get_theme,
    list_themes,
)

__all__ = [
    "quick_report",
    "Report",
    "Theme",
    "get_theme",
    "list_themes",
    "THEME_AMBER_ACADEMIC",
    "THEME_ARCTIC_FROST",
    "THEME_BUSINESS_BLUE",
    "THEME_CLASSIC_WHITE",
    "THEME_CREATIVE_MAGENTA",
    "THEME_FINANCE_CHARCOAL",
    "THEME_FOREST_DAWN",
    "THEME_FRESH_GREEN",
    "THEME_GOVERNMENT_NAVY",
    "THEME_MEDICAL_TEAL",
    "THEME_MIDNIGHT_PLUM",
    "THEME_MINIMAL_GRAY",
    "THEME_OCEAN_DEPTHS",
    "THEME_SAGE_EARTH",
    "THEME_SLATE_PRO",
    "THEME_SUNSET_CORAL",
    "THEME_TECH_DARK",
    "THEME_WARM_ORANGE",
]
__version__ = "0.3.0"
