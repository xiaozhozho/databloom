#!/usr/bin/env python3
"""Custom layout example — using the declarative Report API.

Demonstrates multi-sheet reports with fine-grained control over
element placement, custom column formats, and chart selection.
"""

from pathlib import Path

import pandas as pd

from databloom import Report

output_dir = Path(__file__).resolve().parent.parent / "output"
output_dir.mkdir(parents=True, exist_ok=True)

kpi_df = pd.DataFrame({
    "Metric": ["Total Revenue", "Total Cost", "Net Profit", "Profit Margin", "Avg Order Value"],
    "Q1": [520000, 310000, 210000, 0.404, 1250],
    "Q2": [580000, 340000, 240000, 0.414, 1320],
    "Q3": [560000, 325000, 235000, 0.420, 1280],
})

sales_trend = pd.DataFrame({
    "Month": pd.date_range("2026-01-01", periods=12, freq="ME").strftime("%Y-%m"),
    "Online": [42000, 45000, 48000, 51000, 54000, 57000, 60000, 63000, 66000, 69000, 72000, 75000],
    "Retail": [38000, 39000, 41000, 43000, 44000, 46000, 47000, 49000, 50000, 52000, 53000, 55000],
    "Wholesale": [25000, 26000, 27000, 28000, 29000, 30000, 31000, 32000, 33000, 34000, 35000, 36000],
})

detail_df = pd.DataFrame({
    "Product": [f"SKU-{i:04d}" for i in range(20)],
    "Category": ["Electronics", "Clothing", "Food", "Electronics", "Clothing"] * 4,
    "Price": [299.99, 49.50, 12.99, 399.00, 59.90] * 4,
    "Units Sold": [150, 320, 480, 90, 250] * 4,
    "Revenue": [44998.50, 15840.00, 6235.20, 35910.00, 14975.00] * 4,
})

print("Building custom_layout.xlsx ...")

report = (
    Report(title="2026 Annual Sales Report", theme="warm_orange")
    .add_sheet("Dashboard")
    .add_title("2026 Sales Dashboard")
    .add_subtitle("Key Performance Indicators")
    .add_table(kpi_df, title="Quarterly KPIs",
               column_formats={"Q1": "#,##0", "Q2": "#,##0", "Q3": "#,##0"})
    .add_chart(sales_trend, type="line", category_col="Month",
               value_cols=["Online", "Retail", "Wholesale"],
               title="Monthly Revenue by Channel")
    .add_sheet("Detail Data")
    .add_title("Sales Detail")
    .add_subtitle("Top 20 Products")
    .add_table(detail_df, title="Product Sales Detail",
               column_formats={"Price": "$#,##0.00", "Revenue": "$#,##0.00"})
    .build(output_dir / "custom_layout.xlsx")
)

print(f"Done! Check {output_dir / 'custom_layout.xlsx'}")
