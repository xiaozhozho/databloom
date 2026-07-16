# Claude Code 指引
This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
`databloom` is a Python 3.10+ package for generating beautifully formatted Excel reports using xlsxwriter, pandas, and matplotlib. It provides two usage levels: a quick one-liner via `quick_report(df)` and a declarative builder API via `Report(...)`.

**Version**: 0.3.1 | **Tests**: 524 | **Themes**: 18 | **Chart types**: 9 | **Coverage**: 91%

## Common Commands

```bash
# Install dev environment
pip install -e ".[dev]"

# Run all tests
pytest

# Run a single test file
pytest tests/test_theme/test_presets.py

# Run a single test function
pytest tests/test_theme/test_presets.py::TestBusinessBlue::test_header_is_dark_blue -v

# Run tests with coverage
pytest --cov=databloom --cov-report=term-missing

# Lint & Format
ruff check src/ tests/
ruff format --check src/ tests/
ruff format src/ tests/          # auto-fix formatting

# Type check
mypy src/databloom/

# Run examples
python examples/quick_start.py
python examples/custom_layout.py
python examples/all_themes.py
python examples/finance_report.py
```

## Architecture

The package has a layered architecture (bottom → top):

1. **Theme System** (`theme/`) — visual style definitions. `Theme` dataclass holds all configurable properties (colors, fonts, borders, chart palettes). **18 preset themes** in `presets.py`. Supports JSON/YAML serialization via `to_dict()`/`from_dict()`. `get_theme()` returns **deep copies** — safe to mutate.

2. **Core Engine** (`core/`) — thin wrap over xlsxwriter. `WorkbookManager` handles workbook/sheet lifecycle. `Grid` converts logical grid positions to Excel row/col coordinates.

3. **Element System** (`elements/`) — report content as composable elements. All extend `BaseElement` (ABC with `measure()` → (rows, cols) and `render(workbook, sheet, position)`). Elements: `TitleElement`, `SubtitleElement`, `ParagraphElement`, `TableElement`, `ChartElement`, `ComboChartElement`, `ImageElement`, `SpacerElement`, `_FormulaFooterElement` (internal).

4. **Layout Engine** (`layout/`) — places elements onto sheets. `LayoutEngine` manages page setup. `SheetLayout` manages one sheet's placement. Template presets in `templates.py` (`simple`, `summary_detail`, `dashboard`, `report`).

5. **Smart Facade** (`facade/`) — user-facing API. `Report` class provides a fluid builder (`.add_sheet()`, `.add_title()`, `.add_table()`, `.add_formula_table()`, `.add_chart()`, `.add_combo_chart()`, `.add_image()`, `.add_spacer()`, `.set_page_setup()`, `.apply_template()`, `.build()`). `quick_report(df)` auto-detects DataFrame structure. `Report.quick()` classmethod auto-analyzes DataFrames.

6. **Scheduler** (`scheduler/`) — optional module wrapping `schedule` library. `BloomScheduler` supports daily/weekly/monthly/hourly/minutely report generation. `ReportConfig` dataclass holds report metadata and callbacks.

7. **Data** (`data/`) — 5 built-in business datasets (finance_profit, finance_metrics, sales_orders, hr_workforce, supply_chain). Deterministic random seeds with pickle caching.

8. **Configuration** (`settings.py`) — centralized `BloomSettings` dataclass with 12 sub-sections (Grid, Table, Text, Spacer, Chart, Image, Report, QuickReport, Inspection, DataGeneration, ThemeDefaults, Xlsxwriter). All tunable parameters in one place with `DATABLOOM_*` environment variable overrides.

## Key Design Decisions

- `build(path)` writes to file; `build()` returns `bytes` for web API use
- Chart elements support xlsxwriter native charts (interactive), matplotlib images (static), and **combo charts** (bar+line dual Y-axis)
- Chart types: column, bar, line, pie, doughnut, area, scatter, radar, stock — plus combo
- Themes are deep-copied on retrieval — safe to mutate without polluting global state
- Themes support `to_dict()`/`from_dict()` for JSON/YAML storage and team sharing
- Chart source data is written to **hidden sheets** (`_databloom_chartdata_N`), not visible to users
- Grid positions are 0-indexed logical coordinates; the Grid engine converts to Excel coordinates
- The `elements/` and `layout/` modules operate independently
- Column alignment is auto-inferred from dtype: right for numbers, center for dates, left for strings
- `add_formula_table()` appends native Excel SUM/AVERAGE/MAX/MIN footer rows via xlsxwriter's `write_formula()`
- BloomScheduler uses `schedule` library as optional dependency (`pip install databloom[scheduler]`)
- Built-in datasets are cached as pickle files for reproducible benchmarks and examples

## Testing Strategy

- Integration tests generate real .xlsx files in temp directories, then read back with openpyxl
- `tests/conftest.py` provides shared fixtures: sample DataFrames, temp output paths, theme instances
- Theme presets are exhaustively parameterized across all 18 themes
- Combo chart tests verify render to file without errors
- Serialization tests verify round-trip `to_dict()` → `from_dict()` for multiple themes
- New chart types (doughnut, radar, stock) are tested via parameterized chart type enumeration
