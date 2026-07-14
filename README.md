# excelreport

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A Python framework for generating beautifully formatted Excel reports from pandas DataFrames.

## Features

- **Two modes**: Quick one-liner via `quick_report(df)` or full declarative API
- **Beautiful themes**: 6 built-in color themes (business, fresh, tech, warm, minimal, classic)
- **Tables & Charts**: Rich formatted data tables, native Excel charts + matplotlib images
- **Flexible layout**: Free grid layout with multi-sheet support
- **Smart detection**: Auto-detects DataFrame structure and suggests elements & layouts

## Quick Start

```python
from excelreport import quick_report
import pandas as pd

df = pd.DataFrame({
    "Product": ["Widget A", "Widget B", "Widget C"],
    "Sales": [15000, 23000, 18000],
    "Growth": [0.12, 0.08, 0.15],
})

quick_report(df, output="./output/report.xlsx")
```

## Installation

```bash
pip install excelreport
```

For development:

```bash
pip install -e ".[dev]"
```

## Usage

### Quick Report (Auto Mode)

```python
from excelreport import quick_report

quick_report(df, output="./output/my_report.xlsx", theme="business_blue")
```

### Declarative API

```python
from excelreport import Report

report = (
    Report(title="Monthly Sales Analysis", theme="business_blue")
    .add_sheet("Overview")
    .add_title("2026 Q3 Sales Overview")
    .add_table(summary_df)
    .add_chart(trend_df, type="line", title="Sales Trend")
    .add_sheet("Details")
    .add_title("Sales Details")
    .add_table(detail_df)
    .build("./output/sales_report.xlsx")
)
```

### Available Themes

- `business_blue` — Professional blue headers + alternating gray rows
- `fresh_green` — Fresh greens for eco/health/agriculture
- `tech_dark` — Dark background, white text for tech/data
- `warm_orange` — Warm orange for marketing/creative/retail
- `minimal_gray` — Low saturation grays for formal reports
- `classic_white` — Classic white background, traditional table style

## Development

```bash
# Run tests
pytest

# With coverage
pytest --cov=excelreport --cov-report=term-missing

# Lint
ruff check src/ tests/

# Type check
mypy src/excelreport/
```

## License

MIT — see [LICENSE](LICENSE) for details.
