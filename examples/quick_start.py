#!/usr/bin/env python3
"""Quick start example — the simplest way to generate a report.

This script demonstrates the one-liner `quick_report()` API with a
small sales dataset.
"""

from pathlib import Path

import pandas as pd

from excelreport import quick_report

# ── Sample data ────────────────────────────────────────────────────
sales_df = pd.DataFrame(
    {
        "Product": ["Widget A", "Widget B", "Widget C", "Widget D"],
        "Category": ["Electronics", "Electronics", "Clothing", "Clothing"],
        "Sales": [15000, 23000, 18000, 12000],
        "Cost": [10000, 16000, 13000, 8000],
        "Growth": [0.12, 0.08, 0.15, 0.20],
    }
)

# ── One-liner: auto-detect layout and chart ────────────────────────
output_dir = Path(__file__).resolve().parent.parent / "output"
output_dir.mkdir(parents=True, exist_ok=True)

print("Generating quick_start.xlsx ...")
quick_report(sales_df, output=output_dir / "quick_start.xlsx", theme="business_blue")

# ── Explicit chart type ────────────────────────────────────────────
print("Generating quick_start_line.xlsx ...")
quick_report(
    sales_df,
    output=output_dir / "quick_start_line.xlsx",
    theme="fresh_green",
    chart_type="column",
)

print("Done! Check the output/ directory.")
