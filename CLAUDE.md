# Claude Code 指引
This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
`databloom` is a Python 3.10+ package for generating beautifully formatted Excel reports using xlsxwriter, pandas, and matplotlib. It provides two usage levels: a quick one-liner via `quick_report(df)` and a declarative builder API via `Report(...)`.

**Version**: 0.2.0 | **Tests**: 342 | **Themes**: 10

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

1. **Theme System** (`theme/`) — visual style definitions. `Theme` dataclass holds all configurable properties (colors, fonts, borders, chart palettes). **10 preset themes** in `presets.py`. Supports JSON/YAML serialization via `to_dict()`/`from_dict()`. `get_theme()` returns **deep copies** — safe to mutate.

2. **Core Engine** (`core/`) — thin wrap over xlsxwriter. `WorkbookManager` handles workbook/sheet lifecycle. `Grid` converts logical grid positions to Excel row/col coordinates.

3. **Element System** (`elements/`) — report content as composable elements. All extend `BaseElement` (ABC with `measure()` → (rows, cols) and `render(workbook, sheet, position)`). Elements: `TitleElement`, `SubtitleElement`, `ParagraphElement`, `TableElement`, `ChartElement`, `ComboChartElement`, `ImageElement`, `SpacerElement`.

4. **Layout Engine** (`layout/`) — places elements onto sheets. `LayoutEngine` manages page setup. `SheetLayout` manages one sheet's placement. Template presets in `templates.py` (dashboard fixed in v0.2 — `full_width=False`).

5. **Smart Facade** (`facade/`) — user-facing API. `Report` class provides a fluid builder (`.add_sheet()`, `.add_title()`, `.add_table()`, `.add_combo_chart()`, `.set_page_setup()`, `.add_spacer()`, `.build(path)`). `quick_report(df)` auto-detects DataFrame structure.

5. **Smart Facade** (`facade/`) — user-facing API. `Report` class provides a fluid builder (`.add_sheet()`, `.add_title()`, `.add_table()`, `.add_combo_chart()`, `.set_page_setup()`, `.add_spacer()`, `.build(path)`). `quick_report(df)` auto-detects DataFrame structure.

## Key Design Decisions

- `build(path)` writes to file; `build()` returns `bytes` for web API use
- Chart elements support xlsxwriter native charts (interactive), matplotlib images (static), and **combo charts** (bar+line dual Y-axis)
- Themes are deep-copied on retrieval — safe to mutate without polluting global state
- Themes support `to_dict()`/`from_dict()` for JSON/YAML storage and team sharing
- Chart source data is written to **hidden sheets** (`_databloom_chartdata_N`), not visible to users
- Grid positions are 0-indexed logical coordinates; the Grid engine converts to Excel coordinates
- The `elements/` and `layout/` modules operate independently
- Column alignment is auto-inferred from dtype: right for numbers, center for dates, left for strings

## Testing Strategy

- Integration tests generate real .xlsx files in temp directories, then read back with openpyxl
- `tests/conftest.py` provides shared fixtures: sample DataFrames, temp output paths, theme instances
- Theme presets are exhaustively parameterized across all 10 themes
- Combo chart tests verify render to file without errors
- Serialization tests verify round-trip `to_dict()` → `from_dict()` for multiple themes
