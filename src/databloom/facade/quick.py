"""Quick report generation — one-liner API for rapid Excel reports."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from databloom.facade.report import Report
from databloom.theme.presets import Theme


def quick_report(
    *dataframes: pd.DataFrame,
    output: str | Path | None = None,
    theme: str | Theme | None = None,
    title: str | None = None,
    chart_type: str = "auto",
) -> bytes | None:
    """Generate a styled Excel report from DataFrames in a single call.

    Automatically analyzes each DataFrame's structure and picks the best
    layout and chart types.

    This is a convenience wrapper around ``Report.quick()`` that
    immediately calls ``.build(output)``.

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
    report = Report.quick(
        *dataframes,
        title=title,
        theme=theme,
        chart_type=chart_type,
    )
    return report.build(output)
