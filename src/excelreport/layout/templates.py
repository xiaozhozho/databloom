"""Pre-defined layout templates for common report structures.

Each template function takes a ``LayoutEngine`` and a set of typed
arguments, then places elements in the standard pattern described below.

Templates:
- ``simple``: title → table
- ``summary_detail``: title → summary table → chart → detail table
- ``dashboard``: title → KPI table → multi-chart row
- ``report``: title → paragraph → chart → table → footer (subtitle)
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

import pandas as pd

from excelreport.elements.chart import ChartElement, ChartType
from excelreport.elements.table import TableElement
from excelreport.elements.text import (
    ParagraphElement,
    SubtitleElement,
    TitleElement,
)

if TYPE_CHECKING:
    from excelreport.layout.engine import LayoutEngine


def layout_simple(
    engine: LayoutEngine,
    title: str,
    table_df: pd.DataFrame,
) -> None:
    """Title → Table layout.

    The simplest template — good for quick data dumps with a heading.
    """
    engine.add_sheet("Sheet1")
    engine.place_row(TitleElement(title))
    engine.place_row(TableElement(table_df))


def layout_summary_detail(
    engine: LayoutEngine,
    title: str,
    summary_df: pd.DataFrame,
    chart_df: pd.DataFrame,
    detail_df: pd.DataFrame,
    chart_type: ChartType = "column",
    chart_title: str = "",
) -> None:
    """Title → Summary Table → Chart → Detail Table layout.

    Suitable for reports where you want a high-level overview first,
    followed by a chart and then the full detail data.
    """
    engine.add_sheet("Overview")
    engine.place_row(TitleElement(title))
    engine.place_row(TableElement(summary_df, title="Summary"))
    engine.place_row(ChartElement(chart_df, chart_type=chart_type, title=chart_title))

    engine.add_sheet("Details")
    engine.place_row(TitleElement(f"{title} — Details"))
    engine.place_row(TableElement(detail_df))


def layout_dashboard(
    engine: LayoutEngine,
    title: str,
    kpi_df: pd.DataFrame,
    chart_dfs: Sequence[pd.DataFrame],
    chart_types: Sequence[ChartType] | None = None,
    chart_titles: Sequence[str] | None = None,
) -> None:
    """Title → KPI Table → Chart Row (multiple charts side by side) layout.

    Dashboard-style layout with KPI summary table at top and multiple
    charts arranged in a row below.
    """
    engine.add_sheet("Dashboard")
    engine.place_row(TitleElement(title))
    engine.place_row(TableElement(kpi_df, title="KPIs"))

    # Charts in a row: place first chart, then others on same logical row
    types = chart_types or ["column"] * len(chart_dfs)
    titles = chart_titles or [""] * len(chart_dfs)

    for i, (df, ct, ct_title) in enumerate(zip(chart_dfs, types, titles, strict=False)):
        engine.place(
            ChartElement(df, chart_type=ct, title=ct_title),
            row=engine.current_sheet()._next_row,
            col=i * 1,  # placeholder column offset — Grid handles actual spacing
        )


def layout_report(
    engine: LayoutEngine,
    title: str,
    subtitle: str,
    body_text: str,
    chart_df: pd.DataFrame,
    table_df: pd.DataFrame,
    footer_text: str = "",
    chart_type: ChartType = "column",
    chart_title: str = "",
) -> None:
    """Title → Subtitle → Body Paragraph → Chart → Table → Footer layout.

    Full report layout suitable for formal business reports.
    """
    engine.add_sheet("Report")
    engine.place_row(TitleElement(title))
    engine.place_row(SubtitleElement(subtitle))
    engine.place_row(ParagraphElement(body_text))
    engine.place_row(ChartElement(chart_df, chart_type=chart_type, title=chart_title))
    engine.place_row(TableElement(table_df))
    if footer_text:
        engine.place_row(ParagraphElement(footer_text))
