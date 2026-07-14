"""Declarative Report builder — the main user-facing API for detailed reports."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

from excelreport.layout.engine import LayoutEngine
from excelreport.layout.templates import (
    layout_dashboard,
    layout_report,
    layout_simple,
    layout_summary_detail,
)
from excelreport.theme.presets import Theme, get_theme

if TYPE_CHECKING:
    from excelreport.elements.chart import ChartType


class Report:
    """Fluid builder for creating multi-sheet, multi-element Excel reports.

    Provides a chainable API that mirrors the layout engine:

        Report(title="Analysis", theme="business_blue")
            .add_sheet("Overview")
            .add_title("Sales Report")
            .add_table(summary_df)
            .add_chart(trend_df, type="line")
            .add_sheet("Details")
            .add_table(detail_df)
            .build("./output/report.xlsx")

    If ``build()`` is called without a path it returns ``bytes``, useful
    for serving reports via web APIs.
    """

    def __init__(
        self,
        title: str = "Report",
        theme: str | Theme = "business_blue",
    ) -> None:
        """Initialize the report builder.

        Args:
            title: Report title (used as workbook-level metadata).
            theme: Theme name string or ``Theme`` instance.
        """
        self.title = title
        if isinstance(theme, str):
            self.theme = get_theme(theme)
        else:
            self.theme = theme
        self._engine = LayoutEngine(self.theme)

    def add_sheet(self, name: str) -> Report:
        """Start a new sheet. Subsequent elements are placed on this sheet.

        Args:
            name: The Excel sheet name.

        Returns:
            ``self`` for chaining.
        """
        self._engine.add_sheet(name)
        return self

    def add_title(self, text: str) -> Report:
        """Add a main title element to the current sheet.

        Args:
            text: Title text.

        Returns:
            ``self`` for chaining.
        """
        from excelreport.elements.text import TitleElement

        self._engine.place_row(TitleElement(text))
        return self

    def add_subtitle(self, text: str) -> Report:
        """Add a subtitle element to the current sheet.

        Args:
            text: Subtitle text.

        Returns:
            ``self`` for chaining.
        """
        from excelreport.elements.text import SubtitleElement

        self._engine.place_row(SubtitleElement(text))
        return self

    def add_paragraph(self, text: str) -> Report:
        """Add a body paragraph to the current sheet.

        Args:
            text: Paragraph content.

        Returns:
            ``self`` for chaining.
        """
        from excelreport.elements.text import ParagraphElement

        self._engine.place_row(ParagraphElement(text))
        return self

    def add_table(
        self,
        df: pd.DataFrame,
        *,
        title: str | None = None,
        column_formats: dict[str, str] | None = None,
    ) -> Report:
        """Add a formatted data table to the current sheet.

        Args:
            df: Source DataFrame.
            title: Optional title row above the headers.
            column_formats: Optional custom xlsxwriter format strings per column.

        Returns:
            ``self`` for chaining.
        """
        from excelreport.elements.table import TableElement

        self._engine.place_row(TableElement(df, title=title, column_formats=column_formats))
        return self

    def add_chart(
        self,
        df: pd.DataFrame,
        type: ChartType = "column",
        *,
        category_col: str | None = None,
        value_cols: list[str] | None = None,
        title: str = "",
        backend: str = "xlsxwriter",
    ) -> Report:
        """Add a chart to the current sheet.

        Args:
            df: Source DataFrame.
            type: Chart type (column, bar, line, pie, area, scatter).
            category_col: X-axis column name (auto-detected if omitted).
            value_cols: Y-axis column names (auto-detected if omitted).
            title: Chart title text.
            backend: ``"xlsxwriter"`` or ``"matplotlib"``.

        Returns:
            ``self`` for chaining.
        """
        from excelreport.elements.chart import ChartElement

        self._engine.place_row(
            ChartElement(
                df,
                chart_type=type,
                category_col=category_col,
                value_cols=value_cols,
                title=title,
                backend=backend,  # type: ignore[arg-type]
            )
        )
        return self

    def add_image(
        self,
        image_path: str | Path,
        *,
        scale_x: float = 1.0,
        scale_y: float = 1.0,
    ) -> Report:
        """Insert an image into the current sheet.

        Args:
            image_path: Path to a PNG/JPG file.
            scale_x: Horizontal scale factor.
            scale_y: Vertical scale factor.

        Returns:
            ``self`` for chaining.
        """
        from excelreport.elements.image import ImageElement

        self._engine.place_row(ImageElement(image_path, scale_x=scale_x, scale_y=scale_y))
        return self

    def apply_template(
        self,
        template_name: str,
        **kwargs: object,
    ) -> Report:
        """Apply a named layout template to the current state.

        Note: This clears existing manual placements on the current sheet.

        Args:
            template_name: One of ``"simple"``, ``"summary_detail"``,
                ``"dashboard"``, ``"report"``.
            **kwargs: Template-specific arguments.

        Returns:
            ``self`` for chaining.
        """
        templates: dict[str, object] = {
            "simple": layout_simple,
            "summary_detail": layout_summary_detail,
            "dashboard": layout_dashboard,
            "report": layout_report,
        }
        template_fn = templates.get(template_name)
        if template_fn is None:
            available = ", ".join(templates)
            raise ValueError(f"Template {template_name!r} not found. Available: {available}")

        # The template functions expect a LayoutEngine as first arg
        template_fn(self._engine, **kwargs)  # type: ignore[operator]
        return self

    def build(self, output: str | Path | None = None) -> bytes | None:
        """Render the report and write or return it.

        Args:
            output: File path to write the ``.xlsx``. If ``None``, returns
                the file content as ``bytes``.

        Returns:
            ``bytes`` if ``output`` is ``None``, otherwise ``None`` (file
            written to disk).
        """
        from excelreport.core.workbook import WorkbookManager

        wm = WorkbookManager(output)
        try:
            self._engine.build(wm)
        finally:
            result = wm.close()
        return result
