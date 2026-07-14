"""Table element — renders a pandas DataFrame as a formatted Excel table."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

from excelreport.core.grid import ElementPlacement, Grid
from excelreport.elements.base import BaseElement
from excelreport.theme.base import Theme

if TYPE_CHECKING:
    pass


def _infer_dtype_format(series: pd.Series, theme: Theme) -> str:
    """Infer the best xlsxwriter number format for a Series based on dtype."""
    dtype = series.dtype

    if pd.api.types.is_datetime64_any_dtype(dtype):
        return theme.table.date_format

    if pd.api.types.is_bool_dtype(dtype):
        return ""

    if pd.api.types.is_float_dtype(dtype):
        # Check if it looks like a percentage
        if series.between(0, 1).all() and series.max() <= 1 and series.min() >= 0:
            return theme.table.percent_format
        # Check magnitude for decimal places
        sample = series.dropna()
        if len(sample) > 0:
            max_val = abs(sample.max())
            min_nonzero = abs(sample[sample != 0].min()) if (sample != 0).any() else 1
            if min_nonzero < 0.01 or (max_val < 100 and max_val > 0):
                return "#,##0.00"
        return "#,##0"

    if pd.api.types.is_integer_dtype(dtype):
        return theme.table.number_format

    return ""


def _column_width(col_name: str, series: pd.Series, max_width: int = 30) -> int:
    """Estimate a reasonable column width in characters."""
    # Header width
    header_len = len(str(col_name))
    # Data width — sample up to 100 values
    sample = series.dropna().head(100).astype(str)
    data_max = sample.str.len().max() if len(sample) > 0 else 0
    return min(max(header_len, int(data_max * 0.9)) + 2, max_width)


class TableElement(BaseElement):
    """Renders a pandas DataFrame as a styled Excel data table.

    Features:
    - Theme-aware header row (font, fill, border)
    - Alternating row colors for readability
    - Auto-inferred number/date/percent formatting per column
    - Auto-sized column widths
    - Conditional formatting support (future)

    Example::

        el = TableElement(df, title="Sales Summary")
        rows, cols = el.measure(theme)  # -> (15, 8) for a 14-row, 8-col table
        el.render(wm, sheet, placement, theme)
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        *,
        title: str | None = None,
        height_hint: int = 0,
        width_hint: int = 0,
        column_formats: dict[str, str] | None = None,
        conditional_format_rules: list[dict] | None = None,
    ) -> None:
        """Initialize the table element.

        Args:
            dataframe: Source data.
            title: Optional subtitle row above the header (displayed as a
                merged cell spanning all columns).
            height_hint: Override row count.
            width_hint: Override column count.
            column_formats: Dict mapping column names to custom xlsxwriter
                number format strings.
            conditional_format_rules: Future — list of conditional format
                rule dicts.
        """
        super().__init__(height_hint=height_hint, width_hint=width_hint)
        self.dataframe = dataframe
        self.title = title
        self.column_formats = column_formats or {}
        self.conditional_format_rules = conditional_format_rules or []

    def measure(self, theme: Theme) -> tuple[int, int]:
        rows = len(self.dataframe) + 1  # header + data rows
        if self.title:
            rows += 1
        cols = max(self.width_hint, len(self.dataframe.columns))
        return (rows, cols)

    def render(
        self,
        workbook: object,
        sheet: object,
        placement: ElementPlacement,
        theme: Theme,
    ) -> None:
        wb = getattr(workbook, "wb")
        cache = getattr(workbook, "format_cache")
        ts = theme.table
        df = self.dataframe
        ncols = len(df.columns)

        start_row = placement.start_row
        start_col = placement.start_col
        end_col = start_col + ncols - 1

        current_row = start_row

        # ── Title row (optional) ─────────────────────────────────
        if self.title:
            title_fmt = cache.get(
                wb,
                font_name=ts.header_font.name,
                font_size=ts.header_font.size,
                bold=True,
                font_color=ts.header_font.color,
                bg_color=ts.header_fill.color,
                border=1,
                border_color=ts.header_border.color,
                align="center",
                valign="vcenter",
            )
            sheet.merge_range(  # type: ignore[union-attr]
                current_row, start_col,
                current_row, end_col,
                self.title,
                title_fmt,
            )
            sheet.set_row(current_row, 22)  # type: ignore[union-attr]
            current_row += 1

        # ── Header row ───────────────────────────────────────────
        header_fmt = cache.get(
            wb,
            font_name=ts.header_font.name,
            font_size=ts.header_font.size,
            bold=True,
            font_color=ts.header_font.color,
            bg_color=ts.header_fill.color,
            border=1,
            border_color=ts.header_font.color,  # dark border on header
            align="center",
            valign="vcenter",
            text_wrap=True,
        )
        # Determine column widths
        col_widths: dict[int, int] = {}

        for i, col_name in enumerate(df.columns):
            excel_col = start_col + i
            sheet.write(current_row, excel_col, str(col_name), header_fmt)  # type: ignore[union-attr]
            col_widths[excel_col] = _column_width(str(col_name), df[col_name])

        sheet.set_row(current_row, 24)  # type: ignore[union-attr]
        header_row = current_row
        current_row += 1

        # ── Data rows ────────────────────────────────────────────
        odd_fmt = cache.get(
            wb,
            font_name=ts.data_font.name,
            font_size=ts.data_font.size,
            font_color=ts.data_font.color,
            bg_color=ts.data_fill_odd.color,
            border=1,
            border_color=ts.data_border.color,
            align="left",
            valign="vcenter",
        )
        even_fmt = cache.get(
            wb,
            font_name=ts.data_font.name,
            font_size=ts.data_font.size,
            font_color=ts.data_font.color,
            bg_color=ts.data_fill_even.color,
            border=1,
            border_color=ts.data_border.color,
            align="left",
            valign="vcenter",
        )

        # Build column format cache
        col_fmts: dict[int, object] = {}
        for i, col_name in enumerate(df.columns):
            excel_col = start_col + i
            num_fmt = self.column_formats.get(str(col_name)) or _infer_dtype_format(df[col_name], theme)
            if num_fmt:
                col_fmts[excel_col] = cache.get(
                    wb,
                    font_name=ts.data_font.name,
                    font_size=ts.data_font.size,
                    font_color=ts.data_font.color,
                    num_format=num_fmt,
                    border=1,
                    border_color=ts.data_border.color,
                    align="left",
                    valign="vcenter",
                )

        for row_idx in range(len(df)):
            excel_row = current_row + row_idx
            row_data = df.iloc[row_idx]
            row_bg_fmt = even_fmt if row_idx % 2 == 1 else odd_fmt

            for col_idx in range(ncols):
                excel_col = start_col + col_idx
                value = row_data.iloc[col_idx]

                # Handle NaN / NaT
                if pd.isna(value):
                    sheet.write_blank(excel_row, excel_col, "", row_bg_fmt)  # type: ignore[union-attr]
                    continue

                # Handle Timestamp -> str
                if isinstance(value, pd.Timestamp):
                    value = value.strftime("%Y-%m-%d")

                # Use column-specific format if available
                write_fmt = col_fmts.get(excel_col, row_bg_fmt)
                sheet.write(excel_row, excel_col, value, write_fmt)  # type: ignore[union-attr]

            sheet.set_row(excel_row, 18)  # type: ignore[union-attr]

        # ── Apply column widths ──────────────────────────────────
        for col_idx, width in col_widths.items():
            sheet.set_column(col_idx, col_idx, max(width, 10))  # type: ignore[union-attr]

        # ── Freeze header ────────────────────────────────────────
        freeze_row = header_row + (2 if self.title else 1)
        sheet.freeze_panes(freeze_row, start_col)  # type: ignore[union-attr]

    def needs_full_width(self) -> bool:
        return True
