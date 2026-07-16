# databloom

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A Python framework for generating beautifully formatted Excel reports from pandas DataFrames. Two APIs, one goal: turn your data into presentation-ready spreadsheets in seconds.

## Features

- **Two modes**: `quick_report(df)` one-liner or full `Report` builder API
- **Multi-sheet reports**: fluent builder API for any business domain
- **10 themes**: professionally designed color palettes — business blue, finance charcoal, medical teal, fresh green, creative magenta, warm orange, tech dark, minimal gray, classic white, government navy
- **Tables & Charts**: formatted tables with alternating rows, auto-alignment (numbers right, text left), native Excel charts (column / bar / line / pie / area / scatter), combo charts (bar+line dual Y-axis) + matplotlib image fallback
- **Multi-sheet**: free grid layout with full multi-sheet support, page setup for printing/PDF
- **Smart detection**: auto-infers column types, number formats, alignments, chart types, and layout
- **Built-in datasets**: 5 built-in business datasets (finance, sales, HR, supply chain) — auto-cached as pickle
- **Theme serialization**: JSON/YAML-ready `to_dict()`/`from_dict()` for team sharing and CI/CD
- **Type-safe**: full mypy strict-mode annotations, zero runtime surprises

---

## Installation

```bash
pip install databloom
```

For development:

```bash
pip install -e ".[dev]"
```

---

## Quick Start

### Level 1 — One-liner

```python
from databloom import quick_report
import pandas as pd

df = pd.DataFrame({
    "Product": ["Widget A", "Widget B", "Widget C"],
    "Sales": [15000, 23000, 18000],
    "Growth": [0.12, 0.08, 0.15],
})

quick_report(df, output="./output/report.xlsx")
```

### Level 2 — Declarative Builder

```python
from databloom import Report

report = (
    Report(title="Monthly Sales Analysis", theme="business_blue")
    .set_page_setup(orientation="landscape", fit_to_width=1)
    .add_sheet("Overview")
    .add_title("2026 Q3 Sales Overview")
    .add_table(summary_df)
    .add_combo_chart(
        trend_df,
        category_col="Month",
        bar_cols=["Revenue", "Cost"],
        line_cols=["Margin%"],
        bar_title="Revenue & Cost",
        line_title="Margin %",
        title="Revenue vs Margin",
    )
    .add_sheet("Details")
    .add_title("Product Details")
    .add_table(detail_df)
    .build("./output/sales_report.xlsx")
)
```

---

## Available Themes

| Theme | Key Colour | Font | Best For |
|-------|-----------|------|----------|
| `business_blue` | Deep navy header | Arial | Corporate finance, board decks |
| `finance_charcoal` | Dark gray header, red accent | Lato | Banking, securities, insurance |
| `medical_teal` | Teal green header | Noto Sans | Healthcare, life sciences |
| `fresh_green` | Forest green accents | Calibri | Sustainability, health, agriculture |
| `creative_magenta` | Vibrant magenta | Poppins | Marketing, creative, e-commerce |
| `warm_orange` | Warm amber | Tahoma | Retail, hospitality |
| `government_navy` | Navy blue, formal | Source Sans 3 | Government, public sector, compliance |
| `tech_dark` | Cyan-on-dark | Segoe UI | Tech, data engineering, dashboards |
| `minimal_gray` | Low-contrast neutrals | Helvetica | Legal, compliance, government |
| `classic_white` | Black-on-white | Arial | Traditional print-first reports |

[查看中文文档 →](./README_CN.md)

---

## Customising Themes

You can create, save, and share custom themes:

```python
from databloom import get_theme
import json

# Export a built-in theme as JSON
theme = get_theme("business_blue")
theme.table.data_font.size = 12  # safe to mutate — it's a deep copy!

with open("my_theme.json", "w") as f:
    json.dump(theme.to_dict(), f, indent=2)

# Load a custom theme later
from databloom.theme.base import Theme

with open("my_theme.json") as f:
    custom_theme = Theme.from_dict(json.load(f))

report = Report(title="Custom", theme=custom_theme)
```

---

## API Reference

### `quick_report(*dataframes, output, theme, title, chart_type) → bytes | None`

Auto-analyzes DataFrames and picks the best layout and chart types.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `*dataframes` | `DataFrame` | — | One or more DataFrames to include |
| `output` | `str \| Path \| None` | `None` | File path; `None` returns `bytes` |
| `theme` | `str \| Theme` | `"business_blue"` | Theme name or instance |
| `title` | `str` | `"Quick Report"` | Report title |
| `chart_type` | `str` | `"auto"` | Auto-detect or a specific type |

### `Report(title, theme)` — Builder

| Method | Description |
|--------|-------------|
| `.add_sheet(name)` | Start a new worksheet |
| `.add_title(text)` | Large bold title |
| `.add_subtitle(text)` | Secondary heading |
| `.add_paragraph(text)` | Body text block |
| `.add_table(df, *, title, column_formats, conditional_format_rules)` | Styled data table with smart column alignment |
| `.add_chart(df, type, *, category_col, value_cols, title, backend)` | Native Excel chart (6 chart types) |
| `.add_combo_chart(df, *, category_col, bar_cols, line_cols, bar_title, line_title, title)` | Combo chart (columns + line, dual Y-axis) |
| `.add_image(path, *, scale_x, scale_y)` | Insert PNG/JPG image |
| `.add_spacer(*, rows, height)` | Vertical gap between elements |
| `.set_page_setup(*, orientation, paper, margins, fit_to_width, fit_to_height, print_title_rows)` | Page setup for printing/PDF |
| `.apply_template(template_name, **kwargs)` | Apply a layout template |
| `.build(output=None)` | Render and write / return |


### `load_dataset(name, force_rebuild) → DataFrame | dict`

Load a built-in dataset (first use generates and caches to pickle).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | — | Dataset identifier (see table below) |
| `force_rebuild` | `bool` | `False` | Regenerate even if cached |

### `list_datasets() → list[str]`

Return all available dataset names.

### Built-in Datasets

| Dataset | Rows | Description |
|---------|------|-------------|
| `finance_profit` | 12 | Monthly profit statement |
| `finance_metrics` | 13 | Financial health indicators |
| `sales_orders` | 60 | Sales orders across 10 products |
| `hr_workforce` | 200 | Employee data (dept, level, salary, performance) |
| `supply_chain` | 100 | Procurement orders with supplier quality metrics |

---

## Development

```bash
# Run tests
pytest

# With coverage
pytest --cov=databloom --cov-report=term-missing

# Lint
ruff check src/ tests/
ruff format src/ tests/

# Type check
mypy src/databloom/
```

---

## License

MIT — see [LICENSE](LICENSE) for details.
