"""Quick report generation — one-liner API for rapid Excel reports."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from excelreport.layout.engine import LayoutEngine
from excelreport.layout.templates import layout_report, layout_simple, layout_summary_detail
from excelreport.theme.presets import Theme, get_theme
from excelreport.utils.inspection import profile_dataframe


def quick_report(
    *dataframes: pd.DataFrame,
    output: str | Path | None = None,
    theme: str | Theme = "business_blue",
    title: str = "Quick Report",
    chart_type: str = "auto",
) -> bytes | None:
    """Generate a styled Excel report from DataFrames in a single call.

    Automatically analyzes each DataFrame's structure and picks the best
    layout and chart types.

    Args:
        *dataframes: One or more pandas DataFrames to include.
        output: File path for the ``.xlsx``. If ``None``, returns ``bytes``.
        theme: Theme name or ``Theme`` instance.
        title: Report title (workbook-level).
        chart_type: ``"auto"`` to auto-detect, or a specific chart type
            like ``"column"``, ``"line"``, etc.

    Returns:
        ``bytes`` if ``output`` is ``None``, otherwise ``None`` (file
        written to disk).

    Example::

        quick_report(sales_df, output="./output/sales.xlsx")
        quick_report(kpi_df, detail_df, theme="tech_dark")
    """
    if isinstance(theme, str):
        theme = get_theme(theme)

    from excelreport.core.workbook import WorkbookManager

    engine = LayoutEngine(theme)

    dfs = list(dataframes)

    # No DataFrames provided — minimal template
    if not dfs:
        engine.add_sheet("Sheet1")
        from excelreport.elements.text import TitleElement, ParagraphElement
        engine.place_row(TitleElement(title))
        engine.place_row(ParagraphElement("No data provided."))
        wm = WorkbookManager(output)
        try:
            engine.build(wm)
        finally:
            result = wm.close()
        return result

    # With exactly 1 DataFrame — use simple layout
    if len(dfs) == 1:
        profile = profile_dataframe(dfs[0])

        if profile.suggested_layout == "summary_detail" and len(profile.suggested_chart_types) > 0:
            # Create a summary (first 5 rows) and use the same DF as detail
            summary_df = dfs[0].head(5)
            ct = chart_type if chart_type != "auto" else profile.suggested_chart_types[0]
            ct = ct if ct in ("column", "bar", "line", "pie", "area", "scatter") else "column"
            layout_summary_detail(
                engine, title, summary_df, dfs[0], dfs[0],
                chart_type=ct,  # type: ignore[arg-type]
                chart_title=f"Overview — {profile.columns[0].name if profile.columns else 'Data'}",
            )
        else:
            layout_simple(engine, title, dfs[0])

    # With 2+ DataFrames — summary_detail layout using first as summary, second as detail
    else:
        first = dfs[0]
        second = dfs[1]
        profile = profile_dataframe(first)
        ct = chart_type if chart_type != "auto" else (
            profile.suggested_chart_types[0] if profile.suggested_chart_types else "column"
        )
        ct = ct if ct in ("column", "bar", "line", "pie", "area", "scatter") else "column"
        layout_summary_detail(
            engine, title, first.head(min(10, len(first))),
            first, second,
            chart_type=ct,  # type: ignore[arg-type]
            chart_title="Chart",
        )

    # Write output
    wm = WorkbookManager(output)
    try:
        engine.build(wm)
    finally:
        result = wm.close()
    return result
