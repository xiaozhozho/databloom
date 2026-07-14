"""excelreport — Beautiful Excel reports from pandas DataFrames."""

from excelreport.facade.quick import quick_report
from excelreport.facade.report import Report
from excelreport.theme.base import Theme
from excelreport.theme.presets import (
    THEME_BUSINESS_BLUE,
    THEME_CLASSIC_WHITE,
    THEME_FRESH_GREEN,
    THEME_MINIMAL_GRAY,
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
    "THEME_BUSINESS_BLUE",
    "THEME_CLASSIC_WHITE",
    "THEME_FRESH_GREEN",
    "THEME_MINIMAL_GRAY",
    "THEME_TECH_DARK",
    "THEME_WARM_ORANGE",
]
__version__ = "0.1.0"
