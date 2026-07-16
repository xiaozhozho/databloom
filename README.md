# databloom

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![中文文档](https://img.shields.io/badge/README-%E4%B8%AD%E6%96%87-red)](./README_CN.md)

> Beautiful Excel reports from pandas DataFrames — 18 themes, 9 chart types, smart auto-detection, formula tables, and scheduled generation.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Available Themes](#available-themes)
- [Customising Themes](#customising-themes)
- [API Reference](#api-reference)
- [Built-in Datasets](#built-in-datasets)
- [Development](#development)
- [License](#license)

---

## Features

- **Two modes**: `quick_report(df)` one-liner or full `Report` builder API
- **18 themes**: professionally designed color palettes for finance, healthcare, government, tech, creative, and more
- **9 chart types**: column, bar, line, pie, doughnut, area, scatter, radar, stock — plus combo charts (bar+line dual Y-axis)
- **Smart detection**: auto-infers column types, number formats, alignments, chart types, and layout
- **Formula tables**: append SUM/AVERAGE/MAX/MIN footer rows via native Excel formulas (`add_formula_table()`)
- **Scheduled generation**: `BloomScheduler` for daily/weekly/monthly recurring report jobs
- **Structured tables**: alternating row colors, auto-alignment (numbers right, text left, dates center), freeze panes
- **Combo charts**: bar/column + line on dual Y-axes — ideal for volume-vs-rate dashboards
- **Image insertion**: embed PNG/JPG images from local files
- **Built-in datasets**: 5 business datasets (finance, sales, HR, supply chain) — auto-cached as pickle
- **Theme serialization**: JSON/YAML-ready `to_dict()`/`from_dict()` for team sharing and CI/CD
- **Page setup**: print configuration (orientation, margins, fit-to-pages, repeat headers)
- **Type-safe**: full mypy strict-mode annotations, zero runtime surprises

---

## Installation

```bash
pip install databloom
```

With optional scheduler support:

```bash
pip install "databloom[scheduler]"
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
    .add_formula_table(
        detail_df,
        formulas={"Revenue": "SUM", "Cost": "SUM"},
        formula_label="Total",
    )
    .build("./output/sales_report.xlsx")
)
```

### Level 3 — Scheduled Reports

```python
from databloom.scheduler import BloomScheduler, ReportConfig

config = ReportConfig(
    title="Weekly Sales Dashboard",
    theme="business_blue",
    output_path="./output/weekly_sales.xlsx",
    data_factory=lambda: pd.read_sql("SELECT * FROM sales", conn),
)

scheduler = BloomScheduler()
scheduler.weekly(config, day="monday", at="09:00")
scheduler.start()  # blocking loop — use Ctrl+C to stop
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
| `minimal_gray` | Low-contrast neutrals | Helvetica | Legal, compliance, formal reports |
| `classic_white` | Black-on-white | Arial | Traditional print-first reports |
| `sunset_coral` | Warm coral pink | Nunito | Lifestyle, wellness, hospitality |
| `ocean_depths` | Deep teal blue | Roboto | Maritime, logistics, travel |
| `forest_dawn` | Earthy brown tones | Lora | Education, publishing, nonprofits |
| `slate_pro` | Cool blue-gray | IBM Plex Sans | Engineering, SaaS, B2B tech |
| `amber_academic` | Warm amber brown | Georgia | Academia, research, humanities |
| `midnight_plum` | Deep violet purple | Montserrat | Luxury, fashion, premium brands |
| `sage_earth` | Muted sage green | Work Sans | Wellness, organic, sustainability |
| `arctic_frost` | Icy blue tones | Inter | Nordic design, clean dashboards |

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
| `chart_type` | `str` | `"auto"` | Auto-detect or specific type (column/bar/line/pie/doughnut/area/scatter/radar/stock) |

### `Report(title, theme)` — Builder

| Method | Description |
|--------|-------------|
| `Report.quick(*dfs, title, theme, chart_type)` | Auto-analyze DataFrames, return a `Report` ready to extend or build |
| `.add_sheet(name)` | Start a new worksheet |
| `.add_title(text)` | Large bold title |
| `.add_subtitle(text)` | Secondary heading |
| `.add_paragraph(text)` | Body text block |
| `.add_table(df, *, title, column_formats, freeze_panes)` | Styled data table with smart column alignment |
| `.add_formula_table(df, *, title, formulas, formula_label, freeze_panes)` | Table + auto-computed SUM/AVERAGE/MAX/MIN footer row |
| `.add_chart(df, type, *, category_col, value_cols, title, backend)` | Native Excel chart (9 chart types) |
| `.add_combo_chart(df, *, category_col, bar_cols, line_cols, bar_title, line_title, title)` | Combo chart (columns + line, dual Y-axis) |
| `.add_image(path, *, scale_x, scale_y)` | Insert PNG/JPG image |
| `.add_spacer(*, rows, height)` | Vertical gap between elements |
| `.set_page_setup(*, orientation, paper, margins, fit_to_width, fit_to_height, print_title_rows)` | Page setup for printing/PDF |
| `.apply_template(template_name, **kwargs)` | Apply a layout template |
| `.build(output=None)` | Render and write / return |

### `BloomScheduler` — Scheduled Generation

```python
from databloom.scheduler import BloomScheduler, ReportConfig
```

| Method | Description |
|--------|-------------|
| `scheduler.daily(config, at="09:00")` | Run report every day at specified time |
| `scheduler.weekly(config, day="monday", at="09:00")` | Run report weekly on a given day |
| `scheduler.every_hours(config, hours=1)` | Run report every N hours |
| `scheduler.every_minutes(config, minutes=30)` | Run report every N minutes |
| `scheduler.start()` | Start the blocking scheduler loop |

---

## Built-in Datasets

```python
from databloom.data import load_dataset, list_datasets

print(list_datasets())
# ['finance_metrics', 'finance_profit', 'hr_workforce', 'sales_orders', 'supply_chain']

df = load_dataset("hr_workforce")  # 200 rows × 8 columns
```

| Dataset | Rows | Description |
|---------|------|-------------|
| `finance_profit` | 12 | Monthly profit statement (revenue, cost, profit, margin) |
| `finance_metrics` | 13 | Financial health indicators across 4 categories |
| `sales_orders` | 60 | Sales orders across 10 products, 5 channels, 7 regions |
| `hr_workforce` | 200 | Employee data with 6 departments, 8 levels, performance scores |
| `supply_chain` | 100 | Procurement orders with supplier quality and delivery metrics |

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
