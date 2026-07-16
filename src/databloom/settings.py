"""Centralized configuration for all tunable parameters in databloom.

    All magic numbers, default values, thresholds, and rendering parameters
    are defined here in one convenient place. To customise the defaults:

    .. code-block:: python

        from databloom.settings import settings, BloomSettings

        # Modify individual values at runtime
        settings.chart.default_width = 800
        settings.table.data_row_height = 20

        # Or replace the entire settings object
        custom = BloomSettings()
        custom.grid.margin_top = 4
        # ... assign back to the module singleton

    You can also set environment variables to override settings:

    .. code-block:: bash

        export DATABLOOM_CHART_DEFAULT_WIDTH=800
        export DATABLOOM_REPORT_DEFAULT_THEME=tech_dark
        export DATABLOOM_DATA_MASTER_SEED=42
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

# ═══════════════════════════════════════════════════════════════════════════════
# Grid / Layout settings
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class GridSettings:
    """Spacing, margins, and column widths for the coordinate grid engine.

    These values control the blank space around the edges of each sheet
    and between vertically-stacked elements.
    """

    margin_top: int = 2
    """Number of blank rows between the top of the sheet and the first element."""

    margin_left: int = 1
    """Number of blank columns between the left edge and the first element."""

    element_spacing: int = 2
    """Number of blank rows between vertically-placed elements."""

    default_col_width: float = 16.0
    """Default column width in characters, applied to all used columns."""

    full_width_cols: int = 8
    """Column span for full-width elements (title, table, paragraph, etc.)."""


# ═══════════════════════════════════════════════════════════════════════════════
# Table element settings
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class TableSettings:
    """Rendering parameters for ``TableElement``."""

    # ── Row heights (Excel points) ──────────────────────────────────────
    title_row_height: int = 22
    """Row height for the optional merged title row, in Excel points."""

    header_row_height: int = 24
    """Row height for the data column header row, in Excel points."""

    data_row_height: int = 18
    """Row height for each data row, in Excel points."""

    # ── Column widths (characters) ──────────────────────────────────────
    min_column_width: int = 10
    """Minimum column width in characters (floor applied to auto-sizing)."""

    max_column_width: int = 30
    """Maximum column width in characters (ceiling applied to auto-sizing)."""

    column_width_sample_size: int = 100
    """How many data rows to sample when computing column widths."""

    column_width_char_factor: float = 0.9
    """Multiplier applied to the maximum string length for column width."""

    column_width_padding: int = 2
    """Extra characters added to the computed column width."""

    # ── Freeze panes ────────────────────────────────────────────────────
    freeze_row_offset: int = 2
    """Offset added to the header row for freeze pane (when title present)."""

    freeze_row_offset_no_title: int = 1
    """Offset added to the header row for freeze pane (when no title)."""

    # ── Number format fallbacks ─────────────────────────────────────────
    float_format_decimal: str = "#,##0.00"
    """Format string for floats when decimal precision is warranted."""

    float_format_integer: str = "#,##0"
    """Format string for floats that look like whole numbers."""

    # ── Date format fallback ────────────────────────────────────────────
    timestamp_display_format: str = "%Y-%m-%d"
    """strftime format for displaying pandas Timestamp values."""


# ═══════════════════════════════════════════════════════════════════════════════
# Text element settings
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class TextSettings:
    """Rendering parameters for ``TitleElement``, ``SubtitleElement``,
    and ``ParagraphElement``."""

    title_row_height_factor: float = 2.2
    """Title row height = font_size * this factor (in Excel points)."""

    subtitle_row_height_factor: float = 1.8
    """Subtitle row height = font_size * this factor (in Excel points)."""

    paragraph_row_height_factor: float = 1.6
    """Paragraph row height = font_size * this factor (in Excel points)."""

    paragraph_chars_per_row: int = 80
    """Approximate number of characters that fit in a full-width paragraph row.
    Used by ``ParagraphElement.measure()`` to estimate row count."""


# ═══════════════════════════════════════════════════════════════════════════════
# Spacer element settings
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class SpacerSettings:
    """Defaults for ``SpacerElement``."""

    default_rows: int = 1
    """Default number of logical rows the spacer occupies."""

    default_height: int = 12
    """Default row height in Excel points."""


# ═══════════════════════════════════════════════════════════════════════════════
# Chart element settings
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class ChartSettings:
    """Defaults for ``ChartElement`` and ``ComboChartElement``."""

    # ── Dimensions ──────────────────────────────────────────────────────
    default_width: int = 640
    """Default chart width in pixels (both xlsxwriter and matplotlib)."""

    default_height: int = 400
    """Default chart height in pixels (both xlsxwriter and matplotlib)."""

    rows_per_unit: int = 20
    """Divisor for converting chart height (px) → Excel rows (height/20)."""

    cols_per_unit: int = 60
    """Divisor for converting chart width (px) → Excel columns (width/60)."""

    # ── Matplotlib backend ──────────────────────────────────────────────
    matplotlib_dpi: int = 100
    """Dots-per-inch for matplotlib-rendered charts."""

    figure_facecolor: str = "#FFFFFF"
    """Background color for the matplotlib figure."""

    axes_facecolor: str = "#FFFFFF"
    """Background color for the matplotlib axes."""

    title_fontsize: int = 14
    """Font size for the chart title in matplotlib."""

    title_fontweight: str = "bold"
    """Font weight for the chart title in matplotlib."""

    tick_labelsize: int = 9
    """Font size for axis tick labels in matplotlib."""

    xtick_rotation: int = 45
    """Rotation angle for X-axis tick labels (degrees)."""

    xlabel_ha: str = "right"
    """Horizontal alignment for rotated X-axis labels."""

    yaxis_number_format: str = "{x:,.0f}"
    """Format string for Y-axis numeric labels (matplotlib FuncFormatter)."""

    # ── Matplotlib: chart-type-specific styles ──────────────────────────
    bar_alpha: float = 0.85
    """Transparency (alpha) for column/bar chart fills."""

    bar_width_fraction: float = 0.2
    """Bar width as a fraction of the category interval."""

    bar_group_offset: float = 0.2
    """Offset between grouped bars as a fraction of the category interval."""

    linewidth: float = 2.0
    """Line width for line chart series."""

    markersize: float = 4.0
    """Marker size for line chart data points."""

    scatter_size: float = 40.0
    """Marker size for scatter plot points."""

    scatter_alpha: float = 0.8
    """Transparency (alpha) for scatter plot markers."""

    area_alpha: float = 0.3
    """Transparency (alpha) for area chart fill."""

    pie_autopct: str = "%1.1f%%"
    """Matplotlib ``autopct`` format for pie chart labels."""

    pie_startangle: int = 90
    """Starting angle for pie chart first slice (degrees)."""

    legend_location: str = "best"
    """Matplotlib legend location string."""

    legend_framealpha: float = 0.8
    """Transparency of the legend background."""

    # ── Matplotlib: temp file ───────────────────────────────────────────
    temp_file_suffix: str = ".png"
    """Suffix for temporary chart image files."""

    savefig_bbox_inches: str = "tight"
    """``bbox_inches`` parameter for matplotlib ``savefig()``."""

    savefig_facecolor: str = "white"
    """``facecolor`` parameter for matplotlib ``savefig()``."""

    # ── Combo chart (xlsxwriter) ────────────────────────────────────────
    combo_bar_gap: int = 120
    """Gap between bar groups in xlsxwriter combo charts."""

    combo_line_width: float = 2.5
    """Width for the line series in xlsxwriter combo charts."""

    combo_line_marker_type: str = "circle"
    """Marker type for the line series in xlsxwriter combo charts."""

    combo_line_marker_size: int = 4
    """Marker size for the line series in xlsxwriter combo charts."""

    # ── xlsxwriter chart scale factors (used for render()) ──────────────
    x_scale_factor: float = 1.0
    """X scale factor for xlsxwriter image placement."""

    y_scale_factor: float = 1.0
    """Y scale factor for xlsxwriter image placement."""


# ═══════════════════════════════════════════════════════════════════════════════
# Image element settings
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class ImageSettings:
    """Defaults for ``ImageElement``."""

    default_height_rows: int = 15
    """Default number of Excel rows an image occupies when no hint is given."""

    default_width_cols: int = 10
    """Default number of Excel columns an image occupies when no hint is given."""

    default_scale_x: float = 1.0
    """Default horizontal scale factor for image insertion."""

    default_scale_y: float = 1.0
    """Default vertical scale factor for image insertion."""


# ═══════════════════════════════════════════════════════════════════════════════
# Builder / Facade settings
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class ReportSettings:
    """Defaults for the ``Report`` builder class."""

    default_title: str = "Report"
    """Default workbook-level title text."""

    default_theme_name: str = "business_blue"
    """Default theme name (from presets) when none is specified."""

    # ── Page setup ──────────────────────────────────────────────────────
    page_orientation: str = "landscape"
    """Default page orientation: ``"landscape"`` or ``"portrait"``."""

    page_paper: int = 9
    """Default paper size index.  9 = A4, 1 = US Letter, 13 = B5."""

    page_margin_left: float = 0.7
    """Default left page margin in inches."""

    page_margin_right: float = 0.7
    """Default right page margin in inches."""

    page_margin_top: float = 0.75
    """Default top page margin in inches."""

    page_margin_bottom: float = 0.75
    """Default bottom page margin in inches."""

    page_fit_to_width: int = 1
    """Default ``fit_to_pages`` width (0 = no limit)."""

    page_fit_to_height: int = 0
    """Default ``fit_to_pages`` height (0 = no limit)."""

    page_print_title_rows: int = 0
    """Default number of rows to repeat as header on each printed page."""


@dataclass
class QuickReportSettings:
    """Defaults for ``quick_report()`` one-liner."""

    default_title: str = "Quick Report"
    """Default workbook title."""

    default_theme_name: str = "business_blue"
    """Default theme name (from presets)."""

    default_chart_type: str = "auto"
    """Default chart type selection strategy (``"auto"`` means auto-detect)."""

    summary_head_rows: int = 5
    """Number of rows for the summary table when one DataFrame is provided."""

    max_summary_rows: int = 10
    """Cap on summary rows when two or more DataFrames are provided."""

    supported_chart_types: tuple[str, ...] = (
        "column", "bar", "line", "pie", "doughnut", "area", "scatter", "radar", "stock",
    )
    """Chart types accepted by the auto-detection fallback."""

    no_data_message: str = "No data provided."
    """Default paragraph text when zero DataFrames are passed."""

    default_sheet_name: str = "Sheet1"
    """Default sheet name for the quick report."""


# ═══════════════════════════════════════════════════════════════════════════════
# DataFrame inspection settings
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class InspectionSettings:
    """Thresholds and rules for ``profile_dataframe()``."""

    # ── Categorical detection ───────────────────────────────────────────
    categorical_max_unique: int = 15
    """A string column is treated as categorical if its unique value count ≤ this."""

    categorical_unique_ratio: float = 0.5
    """A string column is treated as categorical only if
    unique / total_rows < this ratio."""

    # ── Layout suggestion thresholds ────────────────────────────────────
    simple_max_cols: int = 5
    """If column count ≤ this AND row count ≤ ``simple_max_rows``, suggest
    ``"simple"`` layout."""

    simple_max_rows: int = 20
    """If row count ≤ this AND column count ≤ ``simple_max_cols``, suggest
    ``"simple"`` layout."""

    summary_detail_max_cols: int = 8
    """If column count ≤ this (but does NOT meet the simple thresholds),
    suggest ``"summary_detail"`` layout.  Otherwise ``"report"``."""

    # ── Chart type suggestions (auto mode) ──────────────────────────────
    temporal_chart_suggestions: tuple[str, ...] = ("line", "column")
    """Suggested chart types when at least 1 temporal + 1 numeric column exist."""

    categorical_chart_suggestions: tuple[str, ...] = ("column", "bar")
    """Suggested chart types when at least 1 categorical + 1 numeric column exist."""

    numeric_only_chart_suggestions: tuple[str, ...] = ("column", "scatter")
    """Suggested chart types when 2+ numeric columns exist with no usable X axis."""


# ═══════════════════════════════════════════════════════════════════════════════
# Synthetic data generation settings
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class DataGenerationSettings:
    """Settings for built-in synthetic data generators."""

    master_seed: int = 2025
    """Master random seed from which all per-dataset seeds are derived.
    Change this to get different synthetic datasets."""

    # Per-dataset seed offsets (derived from master_seed in _seed.py)
    # These are documented here for visibility but *not* used directly;
    # the actual offsets live in ``data/_seed.py``.
    seed_offsets: dict[str, int] = field(default_factory=lambda: {
        "finance_profit": 42,
        "finance_metrics": 43,
        "sales_orders": 100,
        "hr_workforce": 200,
        "supply_chain": 300,
    })


# ═══════════════════════════════════════════════════════════════════════════════
# Theme factory defaults
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class ThemeDefaults:
    """Factory defaults used when constructing a ``Theme`` with no arguments.

    These mirror the ``field(default=...)`` values in the ``Theme`` dataclass
    and its sub-components (``FontSpec``, ``TableStyle``, ``TitleStyle``, etc.).
    They are provided here so you can inspect and override them in one place
    without hunting through ``theme/base.py``.
    """

    name: str = "custom"
    global_font_name: str = "Arial"

    # ── FontSpec defaults ───────────────────────────────────────────────
    font_name: str = "Arial"
    font_size: int = 11
    font_bold: bool = False
    font_italic: bool = False
    font_color: str = "#000000"
    font_underline: bool = False

    # ── FillSpec defaults ───────────────────────────────────────────────
    fill_color: str = "#FFFFFF"
    fill_pattern: int = 1

    # ── BorderSpec defaults ─────────────────────────────────────────────
    border_style: int = 1
    border_color: str = "#D9D9D9"

    # ── TableStyle defaults ─────────────────────────────────────────────
    table_header_font_size: int = 11
    table_header_fill_color: str = "#2F5496"
    table_data_font_size: int = 10
    table_data_fill_odd_color: str = "#FFFFFF"
    table_data_fill_even_color: str = "#F2F2F2"
    table_first_column_font_size: int = 10
    table_number_format: str = "#,##0"
    table_percent_format: str = "0.0%"
    table_date_format: str = "yyyy-mm-dd"
    table_currency_format: str = "#,##0.00"

    # ── TitleStyle defaults ─────────────────────────────────────────────
    title_font_size: int = 18
    title_font_color: str = "#1F3864"

    # ── SubtitleStyle defaults ──────────────────────────────────────────
    subtitle_font_size: int = 13
    subtitle_font_color: str = "#44546A"

    # ── ParagraphStyle defaults ─────────────────────────────────────────
    paragraph_font_size: int = 10
    paragraph_font_color: str = "#333333"

    # ── Layout defaults in Theme ────────────────────────────────────────
    sheet_margin_rows: int = 2
    sheet_margin_cols: int = 1
    element_spacing_rows: int = 2

    # ── Chart palette & accent ──────────────────────────────────────────
    accent_color: str = "#2F5496"
    chart_colors: tuple[str, ...] = (
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
    )

    # ── Alignment defaults ──────────────────────────────────────────────
    title_alignment: str = "left"
    subtitle_alignment: str = "left"
    paragraph_alignment: str = "left"


# ═══════════════════════════════════════════════════════════════════════════════
# Xlsxwriter / workbook constants
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class XlsxwriterSettings:
    """Constants and options for the xlsxwriter library."""

    constant_memory: bool = False
    """Whether to use xlsxwriter's constant-memory mode (off by default)."""

    in_memory: bool = True
    """For byte-output workbooks: whether to use in-memory mode."""

    # Border style constants (convenience aliases)
    BORDER_NONE: int = 0
    BORDER_THIN: int = 1
    BORDER_MEDIUM: int = 2
    BORDER_DASHED: int = 3
    BORDER_DOTTED: int = 4


# ═══════════════════════════════════════════════════════════════════════════════
# Root settings container
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class BloomSettings:
    """All tunable parameters for databloom.

    Use the module-level singleton ``settings`` to read or modify values
    at runtime, or instantiate your own ``BloomSettings`` for a custom
    configuration object.

    Example::

        from databloom.settings import settings

        # Read
        print(settings.chart.default_width)   # 640

        # Override
        settings.grid.margin_top = 0
        settings.table.data_row_height = 20
        settings.chart.default_height = 500
    """

    grid: GridSettings = field(default_factory=GridSettings)
    table: TableSettings = field(default_factory=TableSettings)
    text: TextSettings = field(default_factory=TextSettings)
    spacer: SpacerSettings = field(default_factory=SpacerSettings)
    chart: ChartSettings = field(default_factory=ChartSettings)
    image: ImageSettings = field(default_factory=ImageSettings)
    report: ReportSettings = field(default_factory=ReportSettings)
    quick_report: QuickReportSettings = field(default_factory=QuickReportSettings)
    inspection: InspectionSettings = field(default_factory=InspectionSettings)
    data_gen: DataGenerationSettings = field(default_factory=DataGenerationSettings)
    theme_defaults: ThemeDefaults = field(default_factory=ThemeDefaults)
    xlsxwriter: XlsxwriterSettings = field(default_factory=XlsxwriterSettings)


# ── Module-level singleton ───────────────────────────────────────────────────

settings = BloomSettings()


def reset_settings() -> None:
    """Reset the global settings singleton to factory defaults.

    Useful in test teardown or when you want to discard runtime overrides.
    """
    global settings
    settings = BloomSettings()


# ── Environment variable overrides ───────────────────────────────────────────
# Applied once at import time.  Prefix all vars with ``DATABLOOM_`` and use
# double-underscore as separator for nested dataclass fields.
#
# Examples:
#   DATABLOOM_CHART__DEFAULT_WIDTH=800
#   DATABLOOM_REPORT__DEFAULT_THEME_NAME=tech_dark
#   DATABLOOM_GRID__MARGIN_TOP=0
#   DATABLOOM_TABLE__DATA_ROW_HEIGHT=22
#   DATABLOOM_DATA_GEN__MASTER_SEED=42


def _apply_env_overrides(s: BloomSettings) -> None:
    """Walk settings dataclass fields and apply matching env vars."""
    prefix = "DATABLOOM_"

    for section_name, section in s.__dict__.items():
        if not hasattr(section, "__dataclass_fields__"):
            continue
        for field_name in section.__dataclass_fields__:
            env_key = f"{prefix}{section_name.upper()}__{field_name.upper()}"
            env_val = os.environ.get(env_key)
            if env_val is not None:
                field_type = type(getattr(section, field_name))
                try:
                    if field_type is bool:
                        parsed = env_val.lower() in ("1", "true", "yes")
                    elif field_type is int:
                        parsed = int(env_val)
                    elif field_type is float:
                        parsed = float(env_val)
                    elif field_type in (tuple, list):
                        parsed = tuple(env_val.split(","))
                    else:
                        parsed = env_val
                    setattr(section, field_name, parsed)
                except (ValueError, TypeError):
                    pass  # silently ignore unparseable env vars


_apply_env_overrides(settings)
