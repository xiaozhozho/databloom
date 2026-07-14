"""Abstract base class for all report elements."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from excelreport.core.grid import ElementPlacement
    from excelreport.theme.base import Theme


class BaseElement(ABC):
    """Abstract base for any element that can be placed in a report.

    Subclasses implement ``measure()`` to declare how many Excel rows/cols
    they need, and ``render()`` to write themselves into a worksheet at a
    given placement.

    The ``height_hint`` and ``width_hint`` can be used by the layout engine
    to guide the element's sizing relative to other elements. An element
    may choose to ignore hints if it has fixed requirements (e.g. exactly
    N rows for a table header + data rows).

    Attributes:
        height_hint: Requested row count for the layout engine (0 = auto).
        width_hint: Requested col count for the layout engine (0 = auto).
    """

    def __init__(self, height_hint: int = 0, width_hint: int = 0) -> None:
        self.height_hint = height_hint
        self.width_hint = width_hint

    @abstractmethod
    def measure(self, theme: Theme) -> tuple[int, int]:
        """Return ``(rows, cols)`` this element requires to render.

        Args:
            theme: The active theme — may influence font sizes and thus
                row/column counts.

        Returns:
            A tuple of ``(row_count, column_count)``.
        """
        ...

    @abstractmethod
    def render(
        self,
        workbook: object,
        sheet: object,
        placement: ElementPlacement,
        theme: Theme,
    ) -> None:
        """Write this element into the given worksheet at the placement.

        Args:
            workbook: The xlsxwriter Workbook (or WorkbookManager).
            sheet: The xlsxwriter Worksheet to write into.
            placement: Resolved grid coordinates for this element.
            theme: The active theme to pull styles from.
        """
        ...

    def needs_full_width(self) -> bool:
        """Whether this element should span the full usable width.

        Override in subclasses that naturally stretch across all columns.
        """
        return False
