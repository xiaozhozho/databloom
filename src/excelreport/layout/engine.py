"""Layout engine — places elements onto sheets with grid positioning."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from excelreport.core.grid import ElementPlacement, Grid
from excelreport.elements.base import BaseElement
from excelreport.theme.base import Theme

if TYPE_CHECKING:
    pass


@dataclass
class PlacedElement:
    """An element that has been placed on a sheet, with its resolved position."""

    element: BaseElement
    placement: ElementPlacement
    logical_row: int
    logical_col: int


@dataclass
class SheetLayout:
    """Layout for a single worksheet.

    Tracks elements placed on the sheet, the grid configuration,
    and provides methods for sequential placement.

    Example::

        sl = SheetLayout("Overview", theme)
        sl.place_row(title_el)
        sl.place_row(table_el)
        sl.render(wm, ws)
    """

    sheet_name: str
    theme: Theme
    _elements: list[PlacedElement] = field(default_factory=list)
    _grid: Grid | None = None
    _next_row: int = 0

    def __post_init__(self) -> None:
        self._grid = Grid(
            margin_top=self.theme.sheet_margin_rows,
            margin_left=self.theme.sheet_margin_cols,
            spacing=self.theme.element_spacing_rows,
        )

    @property
    def grid(self) -> Grid:
        if self._grid is None:
            self._grid = Grid(
                margin_top=self.theme.sheet_margin_rows,
                margin_left=self.theme.sheet_margin_cols,
                spacing=self.theme.element_spacing_rows,
            )
        return self._grid

    _DEFAULT_FULL_WIDTH_COLS: int = 8  # default column span for full-width elements

    def place_row(self, element: BaseElement, col_offset: int = 0) -> PlacedElement:
        """Place an element on the next available logical row.

        Elements that ``needs_full_width()`` always start at column 0
        regardless of ``col_offset``.

        Args:
            element: The element to place.
            col_offset: Logical column offset (ignored for full-width elements).

        Returns:
            The placed element with its resolved position.
        """
        logical_row = self._next_row
        logical_col = 0 if element.needs_full_width() else col_offset

        rows, cols = element.measure(self.theme)
        # Ensure full-width elements get a reasonable column span
        if element.needs_full_width() and cols <= 1:
            cols = max(cols, self._DEFAULT_FULL_WIDTH_COLS)

        placement = self.grid.place(logical_row, logical_col, rows, cols)

        placed = PlacedElement(
            element=element,
            placement=placement,
            logical_row=logical_row,
            logical_col=logical_col,
        )
        self._elements.append(placed)

        # Advance next_row for sequential placement
        self._next_row = logical_row + 1

        return placed

    def place_grid(self, element: BaseElement, row: int, col: int) -> PlacedElement:
        """Place an element at a specific logical grid position.

        Args:
            element: The element to place.
            row: Logical row position.
            col: Logical column position.

        Returns:
            The placed element with its resolved position.
        """
        rows, cols = element.measure(self.theme)
        placement = self.grid.place(row, col, rows, cols)

        placed = PlacedElement(
            element=element,
            placement=placement,
            logical_row=row,
            logical_col=col,
        )
        self._elements.append(placed)

        # Keep _next_row past the placed element
        self._next_row = max(self._next_row, row + 1)

        return placed

    def render(self, workbook: object, sheet: object) -> None:
        """Render all placed elements onto the worksheet.

        Args:
            workbook: The WorkbookManager.
            sheet: The target xlsxwriter Worksheet.
        """
        for placed in self._elements:
            placed.element.render(workbook, sheet, placed.placement, self.theme)

        # Apply column widths
        self.grid.write_column_widths(sheet)

    @property
    def element_count(self) -> int:
        return len(self._elements)


class LayoutEngine:
    """Orchestrates layout across multiple sheets.

    The LayoutEngine manages multiple ``SheetLayout`` instances, one
    per Excel sheet. It provides high-level methods for applying
    predefined layout templates.

    Example::

        engine = LayoutEngine(theme)
        engine.add_sheet("Overview")
        engine.add_title("Sales Report")
        engine.add_table(sales_df)
        engine.add_chart(trend_df, type="line")
        engine.add_sheet("Details")
        engine.add_table(details_df)
        engine.build(wm)  # renders all sheets into the workbook
    """

    def __init__(self, theme: Theme) -> None:
        self.theme = theme
        self._sheets: dict[str, SheetLayout] = {}
        self._current_sheet: SheetLayout | None = None

    def add_sheet(self, name: str) -> SheetLayout:
        """Create and switch to a new sheet layout.

        Args:
            name: Sheet name for the Excel worksheet.

        Returns:
            The newly created SheetLayout.

        Raises:
            ValueError: If the sheet name already exists.
        """
        if name in self._sheets:
            raise ValueError(f"Sheet {name!r} already exists.")
        sl = SheetLayout(sheet_name=name, theme=self.theme)
        self._sheets[name] = sl
        self._current_sheet = sl
        return sl

    def current_sheet(self) -> SheetLayout:
        """Return the currently active sheet layout.

        Raises:
            RuntimeError: If no sheet has been added yet.
        """
        if self._current_sheet is None:
            raise RuntimeError("No sheet added. Call add_sheet() first.")
        return self._current_sheet

    def place(self, element: BaseElement, row: int, col: int = 0) -> PlacedElement:
        """Place an element at a specific grid position on the current sheet."""
        return self.current_sheet().place_grid(element, row, col)

    def place_row(self, element: BaseElement) -> PlacedElement:
        """Place an element on the next available row of the current sheet."""
        return self.current_sheet().place_row(element)

    def build(self, workbook: object) -> object:
        """Render all sheets into the workbook.

        Creates each sheet in the workbook and renders its elements.

        Args:
            workbook: A WorkbookManager instance.

        Returns:
            The workbook for method chaining.
        """
        for name, sheet_layout in self._sheets.items():
            ws = None
            # Check if sheet exists, add if not
            if hasattr(workbook, "has_sheet") and callable(workbook.has_sheet):  # type: ignore[arg-type]
                if not workbook.has_sheet(name):  # type: ignore[arg-type]
                    ws = workbook.add_sheet(name)  # type: ignore[arg-type]
                else:
                    ws = workbook.get_sheet(name)  # type: ignore[arg-type]
            else:
                ws = workbook.add_sheet(name)  # type: ignore[attr-defined]

            if ws is not None:
                sheet_layout.render(workbook, ws)

        return workbook
