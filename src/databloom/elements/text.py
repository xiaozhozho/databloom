"""Text-based report elements: title, subtitle, and paragraph."""

from __future__ import annotations

from typing import TYPE_CHECKING

from databloom.core.grid import ElementPlacement
from databloom.elements.base import BaseElement
from databloom.settings import settings
from databloom.theme.base import Theme

if TYPE_CHECKING:
    pass


class TitleElement(BaseElement):
    """A large, bold title for a report or sheet section."""

    def __init__(self, text: str, height_hint: int = 0, width_hint: int = 0) -> None:
        super().__init__(height_hint=height_hint, width_hint=width_hint)
        self.text = text

    def measure(self, theme: Theme) -> tuple[int, int]:
        # Title is always 1 row, spanning to fit its text
        return (1, max(self.width_hint, 1))

    def render(
        self,
        workbook: object,
        sheet: object,
        placement: ElementPlacement,
        theme: Theme,
    ) -> None:
        ts = theme.title
        fmt = workbook.format_cache.get(
            workbook.wb,
            font_name=ts.font.name,
            font_size=ts.font.size,
            bold=ts.font.bold,
            italic=ts.font.italic,
            font_color=ts.font.color,
            align="left",
            valign="vcenter",
        )
        sheet.merge_range(  # type: ignore[union-attr]
            placement.start_row,
            placement.start_col,
            placement.start_row,
            placement.end_col,
            self.text,
            fmt,
        )
        sheet.set_row(placement.start_row, int(ts.font.size * settings.text.title_row_height_factor))  # type: ignore[union-attr]

    def needs_full_width(self) -> bool:
        return True


class SubtitleElement(BaseElement):
    """A secondary heading, smaller than the title."""

    def __init__(self, text: str, height_hint: int = 0, width_hint: int = 0) -> None:
        super().__init__(height_hint=height_hint, width_hint=width_hint)
        self.text = text

    def measure(self, theme: Theme) -> tuple[int, int]:
        return (1, max(self.width_hint, 1))

    def render(
        self,
        workbook: object,
        sheet: object,
        placement: ElementPlacement,
        theme: Theme,
    ) -> None:
        ss = theme.subtitle
        fmt = workbook.format_cache.get(
            workbook.wb,
            font_name=ss.font.name,
            font_size=ss.font.size,
            bold=ss.font.bold,
            italic=ss.font.italic,
            font_color=ss.font.color,
            align="left",
            valign="vcenter",
        )
        sheet.merge_range(  # type: ignore[union-attr]
            placement.start_row,
            placement.start_col,
            placement.start_row,
            placement.end_col,
            self.text,
            fmt,
        )
        sheet.set_row(placement.start_row, int(ss.font.size * settings.text.subtitle_row_height_factor))  # type: ignore[union-attr]

    def needs_full_width(self) -> bool:
        return True


class ParagraphElement(BaseElement):
    """A body text block for descriptions or analysis."""

    def __init__(self, text: str, height_hint: int = 0, width_hint: int = 0) -> None:
        super().__init__(height_hint=height_hint, width_hint=width_hint)
        self.text = text

    def measure(self, theme: Theme) -> tuple[int, int]:
        # Assume N chars per row of text; at least 1 row
        return (max(1, len(self.text) // settings.text.paragraph_chars_per_row + 1), max(self.width_hint, 1))

    def render(
        self,
        workbook: object,
        sheet: object,
        placement: ElementPlacement,
        theme: Theme,
    ) -> None:
        ps = theme.paragraph
        fmt = workbook.format_cache.get(
            workbook.wb,
            font_name=ps.font.name,
            font_size=ps.font.size,
            bold=ps.font.bold,
            italic=ps.font.italic,
            font_color=ps.font.color,
            align="left",
            valign="top",
            text_wrap=True,
        )
        sheet.merge_range(  # type: ignore[union-attr]
            placement.start_row,
            placement.start_col,
            placement.end_row,
            placement.end_col,
            self.text,
            fmt,
        )
        for r in range(placement.start_row, placement.end_row + 1):
            sheet.set_row(r, int(ps.font.size * settings.text.paragraph_row_height_factor))  # type: ignore[union-attr]

    def needs_full_width(self) -> bool:
        return True


class SpacerElement(BaseElement):
    """An empty vertical gap between elements, for manual layout tuning.

    Does not render any content — the layout engine reserves the row
    height and the sheet row is set to the given height.

    Example::

        report.add_sheet("Data")
        report.add_title("Sales Report")
        report.add_spacer(rows=2)  # 2-row gap before the table
        report.add_table(sales_df)
    """

    def __init__(self, *, rows: int | None = None, height: int | None = None) -> None:
        """Initialize the spacer.

        Args:
            rows: How many logical rows the spacer occupies.
            height: Row height in Excel points.
        """
        self.rows = rows if rows is not None else settings.spacer.default_rows
        self.height = height if height is not None else settings.spacer.default_height
        super().__init__(height_hint=self.rows, width_hint=1)

    def measure(self, theme: Theme) -> tuple[int, int]:
        return (max(self.height_hint, 1), 1)

    def render(
        self,
        workbook: object,
        sheet: object,
        placement: ElementPlacement,
        theme: Theme,
    ) -> None:
        for r in range(placement.start_row, placement.end_row + 1):
            sheet.set_row(r, self.height)  # type: ignore[union-attr]

    def needs_full_width(self) -> bool:
        return True
