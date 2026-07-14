"""Tests for Grid coordinate engine."""

from __future__ import annotations

import pytest

from excelreport.core.grid import (
    CellPosition,
    ElementPlacement,
    Grid,
    GridConfig,
)


class TestGridConfig:
    """Tests for GridConfig."""

    def test_defaults(self) -> None:
        gc = GridConfig()
        assert gc.margin_top == 2
        assert gc.margin_left == 1
        assert gc.spacing == 2
        assert gc.default_col_width_chars == 16.0

    def test_custom_values(self) -> None:
        gc = GridConfig(margin_top=0, margin_left=0, spacing=1)
        assert gc.margin_top == 0
        assert gc.margin_left == 0
        assert gc.spacing == 1


class TestColToExcel:
    """Test the static column-number to Excel-letter conversion."""

    def test_0_is_A(self) -> None:
        assert Grid.col_to_excel(0) == "A"

    def test_1_is_B(self) -> None:
        assert Grid.col_to_excel(1) == "B"

    def test_25_is_Z(self) -> None:
        assert Grid.col_to_excel(25) == "Z"

    def test_26_is_AA(self) -> None:
        assert Grid.col_to_excel(26) == "AA"

    def test_27_is_AB(self) -> None:
        assert Grid.col_to_excel(27) == "AB"

    def test_51_is_AZ(self) -> None:
        assert Grid.col_to_excel(51) == "AZ"

    def test_52_is_BA(self) -> None:
        assert Grid.col_to_excel(52) == "BA"

    def test_701_is_ZZ(self) -> None:
        assert Grid.col_to_excel(701) == "ZZ"

    def test_702_is_AAA(self) -> None:
        assert Grid.col_to_excel(702) == "AAA"


class TestCellAddress:
    """Test cell address generation."""

    def test_A1(self) -> None:
        assert Grid.cell_address(0, 0) == "A1"

    def test_B2(self) -> None:
        assert Grid.cell_address(1, 1) == "B2"

    def test_AA10(self) -> None:
        assert Grid.cell_address(9, 26) == "AA10"


class TestGridPlacement:
    """Tests for Grid.place() coordinate resolution."""

    @pytest.fixture
    def grid(self) -> Grid:
        return Grid(margin_top=2, margin_left=1, spacing=2)

    def test_first_placement_starts_at_margins(self, grid: Grid) -> None:
        pos = grid.place(logical_row=0, logical_col=0, rows=5, cols=8)
        assert pos.start_row == 2  # margin_top = 2
        assert pos.start_col == 1  # margin_left = 1
        assert pos.end_row == 6  # start_row + 5 - 1
        assert pos.end_col == 8  # start_col + 8 - 1
        assert pos.row_count == 5
        assert pos.col_count == 8

    def test_second_row_placed_below_with_spacing(self, grid: Grid) -> None:
        p1 = grid.place(0, 0, rows=5, cols=8)
        p2 = grid.place(1, 0, rows=3, cols=8)
        # Row 1 should start after row 0's content + spacing
        expected_start = p1.start_row + p1.row_count + grid.spacing
        assert p2.start_row == expected_start

    def test_same_logical_row_multi_column(self, grid: Grid) -> None:
        p1 = grid.place(0, 0, rows=5, cols=4)
        p2 = grid.place(0, 4, rows=5, cols=4)
        assert p1.start_row == p2.start_row  # same logical row
        assert p2.start_col == 5  # 1 + 4

    def test_different_logical_rows_dont_overlap(self, grid: Grid) -> None:
        p1 = grid.place(0, 0, rows=8, cols=6)
        p2 = grid.place(1, 0, rows=10, cols=6)
        # The second element should start after the first one ends
        assert p2.start_row >= p1.end_row + 1

    def test_zero_height_element(self, grid: Grid) -> None:
        pos = grid.place(0, 0, rows=0, cols=5)
        assert pos.start_row == pos.end_row

    def test_zero_col_element(self, grid: Grid) -> None:
        pos = grid.place(0, 0, rows=5, cols=0)
        assert pos.start_col == pos.end_col

    def test_negative_logical_col_is_allowed(self, grid: Grid) -> None:
        # The grid doesn't restrict this — it's up to the caller
        pos = grid.place(0, -1, rows=1, cols=1)
        assert pos.start_col == 0  # margin_left (1) + (-1) = 0

    def test_total_rows_accumulates(self, grid: Grid) -> None:
        grid.place(0, 0, rows=5, cols=8)
        grid.place(1, 0, rows=3, cols=8)
        # margin_top(2) + row0_height(5) + row1_height(3) = 10
        # Note: spacing is factored into start_row, not into total_rows
        assert grid.total_rows() == 10

    def test_total_cols(self, grid: Grid) -> None:
        grid.place(0, 0, rows=1, cols=4)
        grid.place(0, 4, rows=1, cols=3)
        assert grid.total_cols() == 7
        assert grid.total_excel_cols() == 8  # 7 + margin_left (1)

    def test_spacing_zero(self) -> None:
        g = Grid(margin_top=0, margin_left=0, spacing=0)
        p1 = g.place(0, 0, rows=3, cols=5)
        p2 = g.place(1, 0, rows=2, cols=5)
        # No margin, no spacing: start at 0
        assert p1.start_row == 0
        assert p2.start_row == 3  # right below p1

    def test_write_column_widths(self) -> None:
        """Verify write_column_widths sets columns on a mock sheet."""

        class MockSheet:
            def __init__(self) -> None:
                self.set_calls: list[tuple[int, int, float]] = []

            def set_column(self, first: int, last: int, width: float) -> None:
                self.set_calls.append((first, last, width))

        g = Grid(margin_top=2, margin_left=1, default_col_width=18.5)
        g.place(0, 0, rows=3, cols=5)
        g.place(0, 5, rows=3, cols=2)

        sheet = MockSheet()
        g.write_column_widths(sheet)
        # 7 logical cols + 1 margin_left = 8 excel cols
        assert len(sheet.set_calls) == 8
        for call in sheet.set_calls:
            assert call[0] == call[1]  # one col at a time
            assert call[2] == 18.5


class TestElementPlacement:
    """Tests for ElementPlacement dataclass."""

    def test_fields(self) -> None:
        ep = ElementPlacement(
            start_row=2,
            start_col=1,
            end_row=7,
            end_col=8,
            row_count=6,
            col_count=8,
        )
        assert ep.start_row == 2
        assert ep.end_row == 7
        assert ep.row_count == 6
        assert ep.col_count == 8


class TestCellPosition:
    """Tests for CellPosition dataclass."""

    def test_fields(self) -> None:
        cp = CellPosition(row=0, col=0)
        assert cp.row == 0
        assert cp.col == 0
