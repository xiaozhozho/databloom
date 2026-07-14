#!/usr/bin/env python3
"""All themes demo — generates a report for each of the 6 built-in themes.

Compare visual styles side-by-side to choose the right theme for your brand.
"""

from pathlib import Path

import pandas as pd

from excelreport import Report, list_themes

output_dir = Path(__file__).resolve().parent.parent / "output"
output_dir.mkdir(parents=True, exist_ok=True)

# ── Reusable data ──────────────────────────────────────────────────
summary_df = pd.DataFrame(
    {
        "Region": ["North", "South", "East", "West"],
        "Revenue": [125000, 98000, 142000, 87000],
        "Cost": [75000, 62000, 83000, 54000],
        "Profit": [50000, 36000, 59000, 33000],
    }
)

chart_df = pd.DataFrame(
    {
        "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "Revenue": [42000, 45000, 48000, 51000, 54000, 57000],
        "Target": [40000, 43000, 46000, 49000, 52000, 55000],
    }
)

detail_df = pd.DataFrame(
    {
        "Product": [f"Item-{i:02d}" for i in range(15)],
        "Sales": [120, 95, 140, 80, 110, 135, 70, 155, 100, 125, 90, 145, 105, 130, 85],
        "Stock": [True, True, False, True, True, False, True, True, True, False, True, True, True, False, True],
    }
)

# ── Generate one report per theme ──────────────────────────────────
for theme_name in list_themes():
    filename = f"theme_{theme_name}.xlsx"
    print(f"Generating {filename} ...")

    report = (
        Report(title=f"Theme: {theme_name}", theme=theme_name)
        .add_sheet("Overview")
        .add_title(f"Theme Demo: {theme_name.replace('_', ' ').title()}")
        .add_subtitle("Regional Performance Summary")
        .add_table(summary_df, title="Revenue by Region")
        .add_chart(
            chart_df,
            type="column",
            category_col="Month",
            value_cols=["Revenue", "Target"],
            title="Revenue vs Target",
        )
        .add_sheet("Details")
        .add_title("Product Sales Details")
        .add_table(detail_df, title="Product Performance")
        .build(output_dir / filename)
    )

print(f"\nDone! Generated {len(list_themes())} reports in {output_dir}/")
