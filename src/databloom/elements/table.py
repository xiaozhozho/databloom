"""Table element — renders a pandas DataFrame as a formatted Excel table."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

from databloom.core.grid import ElementPlacement
from databloom.elements.base import BaseElement
from databloom.settings import settings
from databloom.theme.base import Theme

if TYPE_CHECKING:
    from xlsxwriter.worksheet import Worksheet


def _infer_column_alignment(series: pd.Series) -> str:
    """Return the best horizontal alignment for a column based on its dtype.

    - Numeric columns → right-aligned (for financial readability).
    - Datetime columns → center-aligned.
    - String/categorical columns → left-aligned.
    """
    if pd.api.types.is_numeric_dtype(series):
        return "right"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "center"
    return "left"


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
                return settings.table.float_format_decimal
        return settings.table.float_format_integer

    if pd.api.types.is_integer_dtype(dtype):
        return theme.table.number_format

    return ""


def _column_width(col_name: str, series: pd.Series, max_width: int | None = None) -> int:
    """Estimate a reasonable column width in characters."""
    if max_width is None:
        max_width = settings.table.max_column_width
    # Header width
    header_len = len(str(col_name))
    # Data width — sample up to N values
    sample = series.dropna().head(settings.table.column_width_sample_size).astype(str)
    data_max = sample.str.len().max() if len(sample) > 0 else 0
    return min(
        max(header_len, int(data_max * settings.table.column_width_char_factor))
        + settings.table.column_width_padding,
        max_width,
    )


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
        freeze_panes: bool = False,
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
            freeze_panes: Whether to freeze the header row (default False).
        """
        super().__init__(height_hint=height_hint, width_hint=width_hint)
        self.dataframe = dataframe
        self.title = title
        self.column_formats = column_formats or {}
        self.conditional_format_rules = conditional_format_rules or []
        self.freeze_panes = freeze_panes

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
        wb = workbook.wb
        cache = workbook.format_cache
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
                current_row,
                start_col,
                current_row,
                end_col,
                self.title,
                title_fmt,
            )
            sheet.set_row(current_row, settings.table.title_row_height)  # type: ignore[union-attr]
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

        sheet.set_row(current_row, settings.table.header_row_height)  # type: ignore[union-attr]
        header_row = current_row
        current_row += 1

        # ── Data rows ────────────────────────────────────────────
        # Determine per-column alignment
        col_aligns = [_infer_column_alignment(df[col_name]) for col_name in df.columns]

        # Build column format cache
        col_fmts_odd: dict[int, object] = {}
        col_fmts_even: dict[int, object] = {}
        for i, col_name in enumerate(df.columns):
            excel_col = start_col + i
            num_fmt = self.column_formats.get(str(col_name)) or _infer_dtype_format(
                df[col_name], theme
            )
            col_align = col_aligns[i]
            if num_fmt:
                col_fmts_odd[excel_col] = cache.get(
                    wb,
                    font_name=ts.data_font.name,
                    font_size=ts.data_font.size,
                    font_color=ts.data_font.color,
                    bg_color=ts.data_fill_odd.color,
                    num_format=num_fmt,
                    border=1,
                    border_color=ts.data_border.color,
                    align=col_align,
                    valign="vcenter",
                )
                col_fmts_even[excel_col] = cache.get(
                    wb,
                    font_name=ts.data_font.name,
                    font_size=ts.data_font.size,
                    font_color=ts.data_font.color,
                    bg_color=ts.data_fill_even.color,
                    num_format=num_fmt,
                    border=1,
                    border_color=ts.data_border.color,
                    align=col_align,
                    valign="vcenter",
                )

        # First-column formats (bold per theme, with alternating backgrounds)
        # Use the first column's natural alignment
        first_col_align = col_aligns[0] if col_aligns else "left"
        first_col_fmt_odd = cache.get(
            wb,
            font_name=ts.first_column_font.name,
            font_size=ts.first_column_font.size,
            bold=ts.first_column_font.bold,
            italic=ts.first_column_font.italic,
            font_color=ts.first_column_font.color,
            bg_color=ts.data_fill_odd.color,
            border=1,
            border_color=ts.data_border.color,
            align=first_col_align,
            valign="vcenter",
        )
        first_col_fmt_even = cache.get(
            wb,
            font_name=ts.first_column_font.name,
            font_size=ts.first_column_font.size,
            bold=ts.first_column_font.bold,
            italic=ts.first_column_font.italic,
            font_color=ts.first_column_font.color,
            bg_color=ts.data_fill_even.color,
            border=1,
            border_color=ts.data_border.color,
            align=first_col_align,
            valign="vcenter",
        )

        for row_idx in range(len(df)):
            excel_row = current_row + row_idx
            row_data = df.iloc[row_idx]
            is_odd = row_idx % 2 == 0

            for col_idx in range(ncols):
                excel_col = start_col + col_idx
                value = row_data.iloc[col_idx]

                # Pick format: first-column bold, column-specific, or default row bg
                if col_idx == 0 and not self.column_formats.get(str(df.columns[0])):
                    row_col_fmt = first_col_fmt_odd if is_odd else first_col_fmt_even
                elif is_odd and excel_col in col_fmts_odd:
                    row_col_fmt = col_fmts_odd[excel_col]
                elif not is_odd and excel_col in col_fmts_even:
                    row_col_fmt = col_fmts_even[excel_col]
                else:
                    # Default row bg with per-column alignment
                    col_align = col_aligns[col_idx]
                    if is_odd:
                        row_col_fmt = cache.get(
                            wb,
                            font_name=ts.data_font.name,
                            font_size=ts.data_font.size,
                            font_color=ts.data_font.color,
                            bg_color=ts.data_fill_odd.color,
                            border=1,
                            border_color=ts.data_border.color,
                            align=col_align,
                            valign="vcenter",
                        )
                    else:
                        row_col_fmt = cache.get(
                            wb,
                            font_name=ts.data_font.name,
                            font_size=ts.data_font.size,
                            font_color=ts.data_font.color,
                            bg_color=ts.data_fill_even.color,
                            border=1,
                            border_color=ts.data_border.color,
                            align=col_align,
                            valign="vcenter",
                        )

                # Handle NaN / NaT
                if pd.isna(value):
                    sheet.write_blank(excel_row, excel_col, "", row_col_fmt)  # type: ignore[union-attr]
                    continue

                # Handle Timestamp -> str
                if isinstance(value, pd.Timestamp):
                    value = value.strftime(settings.table.timestamp_display_format)

                sheet.write(excel_row, excel_col, value, row_col_fmt)  # type: ignore[union-attr]

            sheet.set_row(excel_row, settings.table.data_row_height)  # type: ignore[union-attr]

        # ── Apply column widths ──────────────────────────────────
        for col_idx, width in col_widths.items():
            sheet.set_column(col_idx, col_idx, max(width, settings.table.min_column_width))  # type: ignore[union-attr]

        # ── Conditional formatting ────────────────────────────────
        if self.conditional_format_rules:
            data_start_row = header_row + 1
            data_end_row = data_start_row + len(df) - 1
            for rule in self.conditional_format_rules:
                sheet.conditional_format(  # type: ignore[union-attr]
                    data_start_row,
                    start_col,
                    data_end_row,
                    end_col,
                    rule,
                )

        # ── Freeze header ────────────────────────────────────────
        if self.freeze_panes:
            freeze_row = header_row + (
                settings.table.freeze_row_offset if self.title else settings.table.freeze_row_offset_no_title
            )
            sheet.freeze_panes(freeze_row, start_col)  # type: ignore[union-attr]

    def needs_full_width(self) -> bool:
        return True


# ═══════════════════════════════════════════════════════════════════════
# Formula Footer Element (used by Report.add_formula_table)
# ═══════════════════════════════════════════════════════════════════════


class _FormulaFooterElement(BaseElement):
    """Internal element that renders a formula summary row below a table.

    This is not part of the public API — use ``Report.add_formula_table()``
    to add a table with formulas in one call.
    """

    FORMULA_PREFIXES: dict[str, str] = {
        "SUM": "=SUM({col_letter}{data_start}:{col_letter}{data_end})",
        "AVERAGE": "=AVERAGE({col_letter}{data_start}:{col_letter}{data_end})",
        "MAX": "=MAX({col_letter}{data_start}:{col_letter}{data_end})",
        "MIN": "=MIN({col_letter}{data_start}:{col_letter}{data_end})",
    }

    def __init__(
        self,
        df: pd.DataFrame,
        formulas: dict[str, str],
        formula_label: str = "Total",
        bold_formulas: bool = True,
        height_hint: int = 0,
        width_hint: int = 0,
    ) -> None:
        super().__init__(height_hint=height_hint, width_hint=width_hint)
        self.df = df
        self.formulas = formulas
        self.formula_label = formula_label
        self.bold_formulas = bold_formulas

    def measure(self, theme: Theme) -> tuple[int, int]:
        rows = 1  # single footer row
        cols = max(self.width_hint, len(self.df.columns))
        return (rows, cols)

    def render(
        self,
        workbook: object,
        sheet: object,
        placement: ElementPlacement,
        theme: Theme,
    ) -> None:
        wb = workbook.wb
        cache = workbook.format_cache
        ts = theme.table
        ncols = len(self.df.columns)
        data_start = placement.start_row - len(self.df)
        data_end = data_start + len(self.df)
        formula_start = placement.start_row
        formula_col = placement.start_col

        # Build format for formula row
        fmt = cache.get(
            wb,
            font_name=ts.data_font.name,
            font_size=ts.data_font.size,
            bold=self.bold_formulas,
            font_color=ts.header_font.color,
            bg_color=ts.header_fill.color,
            border=1,
            border_color=ts.header_border.color,
            align="right",
            valign="vcenter",
        )
        label_fmt = cache.get(
            wb,
            font_name=ts.data_font.name,
            font_size=ts.data_font.size,
            bold=self.bold_formulas,
            font_color=ts.header_font.color,
            bg_color=ts.header_fill.color,
            border=1,
            border_color=ts.header_border.color,
            align="left",
            valign="vcenter",
        )

        # Set the formula row height
        sheet.set_row(formula_start, settings.table.data_row_height)

        for col_idx, col_name in enumerate(self.df.columns):
            excel_col = formula_col + col_idx
            col_letter = _col_letter(excel_col)

            if col_idx == 0 and self.formula_label:
                # First column: label text
                sheet.write(formula_start, excel_col, self.formula_label, label_fmt)
            elif str(col_name) in self.formulas:
                formula_key = self.formulas[str(col_name)]
                # Check if it's a built-in prefix or custom formula
                if formula_key in self.FORMULA_PREFIXES:
                    formula_str = self.FORMULA_PREFIXES[formula_key].format(
                        col_letter=col_letter,
                        data_start=data_start + 1,    # xlsxwriter rows are 0-indexed
                        data_end=data_end,
                    )
                else:
                    formula_str = formula_key
                sheet.write_formula(formula_start, excel_col, formula_str, fmt)
            else:
                # Empty cell for columns without formula
                sheet.write_blank(formula_start, excel_col, "", fmt)

    def needs_full_width(self) -> bool:
        return True


def _col_letter(col: int) -> str:
    """Convert a 0-indexed column number to Excel column letter(s)."""
    result = ""
    while col >= 0:
        result = chr(ord("A") + col % 26) + result
        col = col // 26 - 1
    return result
