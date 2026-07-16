"""Sparkline element — in-cell mini trend charts.

xlsxwriter natively supports sparklines (line, column, win_loss types)
via :meth:`Worksheet.add_sparkline`. This element wraps that API for
the databloom element system.

Example::

    from databloom.elements.sparkline import SparklineElement

    df = pd.DataFrame({
        "Product": ["A", "B", "C"],
        "Jan": [100, 200, 150],
        "Feb": [120, 180, 170],
        "Mar": [130, 190, 180],
    })

    # One sparkline per row, placed in the "Trend" column
    el = SparklineElement(
        df[["Jan", "Feb", "Mar"]],
        destination_col=1,  # column index for sparkline placement
        sparkline_type="line",
    )
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import pandas as pd

from databloom.core.grid import ElementPlacement
from databloom.elements.base import BaseElement
from databloom.theme.base import Theme

if TYPE_CHECKING:
    pass

SparklineType = Literal["line", "column", "win_loss"]


class SparklineElement(BaseElement):
    """Renders sparklines (in-cell mini charts) from a DataFrame of numeric data.

    Each row in the input DataFrame becomes one sparkline.  The data range
    is written to a hidden helper sheet (``_databloom_sparklines``) so that
    the sparkline formula range refers to real worksheet data.  The sparklines
    are placed in a designated column of the visible sheet.

    Sparklines are Excel-native — interactive, scalable, and zero rendering
    overhead compared to image-based mini charts.

    Args:
        data: A ``DataFrame`` containing **only numeric columns**.  Each row
            becomes one sparkline.
        destination_col: Zero-based column index where the sparklines should
            be placed on the visible sheet.
        sparkline_type: One of ``"line"``, ``"column"``, or ``"win_loss"``.
        low_point: Highlight the lowest data point (line/column only).
        high_point: Highlight the highest data point (line/column only).
        first_point: Highlight the first data point (line/column only).
        last_point: Highlight the last data point (line/column only).
        negative_points: Highlight negative values (line/column only).
        markers: Show data markers (line type only).
        line_weight: Sparkline line weight in points (line type only).
    """

    def __init__(
        self,
        data: pd.DataFrame,
        *,
        destination_col: int = 0,
        sparkline_type: SparklineType = "line",
        low_point: bool = False,
        high_point: bool = False,
        first_point: bool = False,
        last_point: bool = False,
        negative_points: bool = False,
        markers: bool = False,
        line_weight: float = 1.0,
        height_hint: int = 0,
    ) -> None:
        super().__init__(height_hint=height_hint, width_hint=0)
        self.data = data
        self.destination_col = destination_col
        self.sparkline_type: SparklineType = sparkline_type
        self.low_point = low_point
        self.high_point = high_point
        self.first_point = first_point
        self.last_point = last_point
        self.negative_points = negative_points
        self.markers = markers
        self.line_weight = line_weight

    def measure(self, theme: Theme) -> tuple[int, int]:
        """Each data row → one sparkline row."""
        nrows = len(self.data)
        ncols = self.data.shape[1] + 1  # data columns + sparkline column
        return (nrows, ncols)

    def render(
        self,
        workbook: object,
        sheet: object,
        placement: ElementPlacement,
        theme: Theme,
    ) -> None:
        num_rows = len(self.data)
        if num_rows == 0:
            return

        num_data_cols = self.data.shape[1]

        # ── Write source data to a hidden helper sheet ────────────────────
        wb = workbook.wb
        # Use a unique suffix to avoid collisions with multiple sparkline
        # elements in the same report
        sheet_name = f"_databloom_sparklines_{id(self):x}"
        data_sheet = wb.add_worksheet(sheet_name)
        data_sheet.hide()

        for row_idx in range(num_rows):
            for col_idx in range(num_data_cols):
                val = self.data.iloc[row_idx, col_idx]
                try:
                    float_val = float(val)
                    data_sheet.write_number(row_idx, col_idx, float_val)
                except (ValueError, TypeError):
                    data_sheet.write_blank(row_idx, col_idx, "")

        # ── Place sparklines on the visible sheet ─────────────────────────
        dest_col = placement.start_col + self.destination_col

        location_list: list[str] = []
        range_list: list[str] = []

        for row_idx in range(num_rows):
            sheet_row = placement.start_row + row_idx
            location_list.append(_cell_address(sheet_row, dest_col))
            range_list.append(
                _sparkline_range(
                    sheet_name,
                    row_idx,
                    0,
                    row_idx,
                    num_data_cols - 1,
                )
            )

        # Use the first cell as the primary location, then pass lists
        sparkline_params: dict = {
            "location": location_list,
            "range": range_list,
        }

        if self.sparkline_type == "column":
            sparkline_params["type"] = "column"
        elif self.sparkline_type == "win_loss":
            sparkline_params["type"] = "win_loss"
        # "line" is the default type — no explicit type key needed

        if self.sparkline_type in ("line", "column"):
            sparkline_params["low_point"] = self.low_point
            sparkline_params["high_point"] = self.high_point
            sparkline_params["first_point"] = self.first_point
            sparkline_params["last_point"] = self.last_point
            sparkline_params["negative_points"] = self.negative_points

            if self.sparkline_type == "line":
                sparkline_params["markers"] = self.markers
                sparkline_params["weight"] = self.line_weight

        sheet.add_sparkline(location_list[0], sparkline_params)  # type: ignore[union-attr]

    def needs_full_width(self) -> bool:
        return False


def _sparkline_range(
    sheet_name: str,
    row_first: int,
    col_first: int,
    row_last: int,
    col_last: int,
) -> str:
    """Build an A1-style range string for a sparkline data source."""
    import xlsxwriter.utility as xu

    first = xu.xl_rowcol_to_cell(row_first, col_first, row_abs=True, col_abs=True)
    last = xu.xl_rowcol_to_cell(row_last, col_last, row_abs=True, col_abs=True)
    return f"={sheet_name}!${first}:${last}"


def _cell_address(row: int, col: int) -> str:
    """Build an absolute cell reference (e.g. ``$A$1``)."""
    import xlsxwriter.utility as xu

    return xu.xl_rowcol_to_cell(row, col, row_abs=True, col_abs=True)
