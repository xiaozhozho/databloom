"""Grid coordinate engine for mapping logical layout to Excel positions.

The Grid system uses 0-indexed logical coordinates:
- ``row`` / ``col`` are logical grid positions (element placements).
- The engine converts them to Excel row/column numbers accounting for
  margins, element heights/widths, and spacing.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CellPosition:
    """A resolved Excel cell position (real row, real col)."""

    row: int  # zero-indexed Excel row
    col: int  # zero-indexed Excel column


@dataclass
class ElementPlacement:
    """Where an element is placed on a sheet, in Excel coordinates."""

    start_row: int
    start_col: int
    end_row: int  # inclusive
    end_col: int  # inclusive
    row_count: int  # how many rows the element occupies
    col_count: int  # how many cols the element occupies


@dataclass
class GridConfig:
    """Configuration for the grid coordinate engine.

    Attributes:
        margin_top: Blank rows at the top of the sheet before content.
        margin_left: Blank columns to the left of content.
        spacing: Blank rows between elements placed vertically.
        default_col_width_chars: Default column width in characters
            (applied to all used columns).
    """

    margin_top: int = 2
    margin_left: int = 1
    spacing: int = 2
    default_col_width_chars: float = 16.0


@dataclass
class _RowTracker:
    """Internal: tracks usage of logical rows and maps to Excel rows."""

    _entries: list[tuple[int, int]] = field(default_factory=list)
    # Each entry: (logical_row, height_in_excel_rows)

    def place(self, logical_row: int, height: int) -> int:
        """Record a placement and return the Excel row offset.

        Returns the start Excel row for this logical row position.
        """
        self._entries.append((logical_row, height))
        return self._compute_offset(logical_row)

    def total_rows(self) -> int:
        """Total Excel rows consumed by all placements."""
        if not self._entries:
            return 0
        return max(self._compute_offset(lr) + h for lr, h in self._entries)

    def _compute_offset(self, target_logical_row: int) -> int:
        """Sum heights of entries with logical_row < target."""
        return sum(h for lr, h in self._entries if lr < target_logical_row)


class Grid:
    """Maps logical grid positions to absolute Excel row/column coordinates.

    A logical position ``(row, col)`` represents the element's placement
    in the layout. The Grid converts these to actual Excel coordinates
    by summing up the heights/widths of preceding logical rows/columns
    and adding margins.

    Example::

        g = Grid(margin_top=2, margin_left=1, spacing=2)
        # Place a 5-row element at logical row 0
        pos = g.place(0, 0, rows=5, cols=8)
        # pos.start_row == 2, pos.start_col == 1
        # Place a 3-row element at logical row 1 (will land below the first)
        pos2 = g.place(1, 0, rows=3, cols=8)
        # pos2.start_row == 7 + 2(spacing) = 9
    """

    def __init__(
        self,
        margin_top: int = 2,
        margin_left: int = 1,
        spacing: int = 2,
        default_col_width: float = 16.0,
    ) -> None:
        self.margin_top = margin_top
        self.margin_left = margin_left
        self.spacing = spacing
        self.default_col_width = default_col_width
        self._row_tracker = _RowTracker()
        self._total_cols_used: int = 0

    def place(
        self,
        logical_row: int,
        logical_col: int,
        rows: int,
        cols: int,
    ) -> ElementPlacement:
        """Reserve a rectangular region in the grid.

        Args:
            logical_row: Which logical row to place at (0-indexed).
            logical_col: Which logical column to place at (0-indexed).
            rows: Number of Excel rows the element needs.
            cols: Number of Excel columns the element needs.

        Returns:
            The resolved Excel coordinate placement.
        """
        start_row = (
            self.margin_top
            + self.spacing * logical_row
            + self._row_tracker.place(logical_row, rows)
        )
        start_col = self.margin_left + logical_col

        end_row = start_row + max(rows - 1, 0)
        end_col = start_col + max(cols - 1, 0)

        total_cols = logical_col + max(cols, 0)
        if total_cols > self._total_cols_used:
            self._total_cols_used = total_cols

        return ElementPlacement(
            start_row=start_row,
            start_col=start_col,
            end_row=end_row,
            end_col=end_col,
            row_count=rows,
            col_count=cols,
        )

    def total_rows(self) -> int:
        """Total Excel rows consumed by all placed elements (plus margins)."""
        return self.margin_top + self._row_tracker.total_rows()

    def total_cols(self) -> int:
        """Total logical columns used."""
        return max(self._total_cols_used, 0)

    def total_excel_cols(self) -> int:
        """Total Excel columns used (logical cols + left margin)."""
        return self.margin_left + self._total_cols_used

    def write_column_widths(self, sheet: object) -> None:
        """Apply default column widths to all used columns.

        Args:
            sheet: An xlsxwriter worksheet object (duck-typed).
        """
        for c in range(self.total_excel_cols()):
            sheet.set_column(c, c, self.default_col_width)  # type: ignore[union-attr]

    @staticmethod
    def col_to_excel(col: int) -> str:
        """Convert a 0-indexed column number to Excel column letter(s).

        0 -> 'A', 1 -> 'B', 26 -> 'AA', etc.
        """
        result = ""
        n = col
        while n >= 0:
            result = chr(65 + n % 26) + result
            n = n // 26 - 1
        return result

    @staticmethod
    def cell_address(row: int, col: int) -> str:
        """Return an Excel A1-style cell address.

        Args:
            row: 0-indexed row.
            col: 0-indexed column.

        Returns:
            e.g. ``"A1"``, ``"AA3"``.
        """
        return f"{Grid.col_to_excel(col)}{row + 1}"
