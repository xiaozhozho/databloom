# Claude Code 指引
This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
`excelreport` is a Python 3.10+ package for generating beautifully formatted Excel reports using xlsxwriter, pandas, and matplotlib. It provides two usage modes: a quick one-liner via `quick_report(df)`, and a declarative builder API via `Report(...).add_sheet(...).add_table(...).build()`.

## Common Commands

```bash
# Install dev environment
pip install -e ".[dev]"

# Run all tests
pytest

# Run a single test file
pytest tests/test_theme/test_presets.py

# Run a single test function
pytest tests/test_theme/test_presets.py::test_business_blue_theme -v

# Run tests with coverage
pytest --cov=excelreport --cov-report=term-missing

# Lint & Format
ruff check src/ tests/
ruff format --check src/ tests/
ruff format src/ tests/          # auto-fix formatting

# Type check
mypy src/excelreport/

# Run examples
python examples/quick_start.py
python examples/custom_layout.py
python examples/all_themes.py
```

## Architecture

The package has a layered architecture (bottom → top):

1. **Theme System** (`theme/`) — visual style definitions. `Theme` dataclass holds all configurable properties (colors, fonts, borders, chart palettes). Six preset themes in `presets.py`. All other layers take a `Theme` instance.

2. **Core Engine** (`core/`) — thin wrap over xlsxwriter. `WorkbookManager` handles workbook/sheet lifecycle. `Grid` converts logical grid positions to Excel row/col coordinates.

3. **Element System** (`elements/`) — report content as composable elements. All extend `BaseElement` (ABC with `measure()` → (rows, cols) and `render(workbook, sheet, position)`). Elements: `TitleElement`, `SubtitleElement`, `ParagraphElement`, `TableElement`, `ChartElement`, `ImageElement`, `SpacerElement`.

4. **Layout Engine** (`layout/`) — places elements onto sheets. `LayoutEngine` handles placement, spacing, collision avoidance. `SheetLayout` manages one sheet's layout. Template presets in `templates.py`.

5. **Smart Facade** (`facade/`) — user-facing API. `Report` class provides a fluid builder (chain `.add_sheet()`, `.add_title()`, `.add_table()`, `.add_chart()`, etc., then call `.build(path)`. `quick_report(df)` auto-detects DataFrame structure and generates a report in one call.

## Key Design Decisions

- `build(path)` writes to file; `build()` returns `bytes` for web API use
- Chart elements support both xlsxwriter native charts (interactive) and matplotlib-rendered images (prettier but static)
- Themes can be partially overridden — theme is the default, individual elements accept overrides
- Grid positions are 0-indexed logical coordinates; the Grid engine converts to Excel coordinates accounting for margins and spacing
- The `elements/` and `layout/` modules operate independently — you can use elements without the layout engine, and vice versa

## Testing Strategy

- Unit tests mock xlsxwriter calls to verify formatting without writing files
- Integration tests generate real .xlsx files in temp directories, then read back with openpyxl to verify structure
- `tests/conftest.py` provides shared fixtures: sample DataFrames, temp output paths, theme instances
