"""Tests for Report builder (declarative API)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from databloom import Report
from databloom.theme.presets import THEME_BUSINESS_BLUE, THEME_TECH_DARK


class TestReportBuilder:
    """Tests for the Report builder class."""

    def test_create_defaults(self) -> None:
        r = Report()
        assert r.title == "Report"
        assert r.theme == THEME_BUSINESS_BLUE

    def test_create_with_theme_string(self) -> None:
        r = Report(theme="tech_dark")
        assert r.theme == THEME_TECH_DARK

    def test_create_with_theme_object(self) -> None:
        r = Report(theme=THEME_TECH_DARK)
        assert r.theme == THEME_TECH_DARK

    def test_create_with_invalid_theme(self) -> None:
        with pytest.raises(KeyError):
            Report(theme="nonexistent")

    def test_add_sheet_returns_self(self) -> None:
        r = Report()
        result = r.add_sheet("Data")
        assert result is r

    def test_add_title_returns_self(self) -> None:
        r = Report().add_sheet("S")
        assert r.add_title("Hello") is r

    def test_add_table_returns_self(self) -> None:
        r = Report().add_sheet("S")
        df = pd.DataFrame({"A": [1]})
        assert r.add_table(df) is r

    def test_add_chart_returns_self(self) -> None:
        r = Report().add_sheet("S")
        df = pd.DataFrame({"X": [1, 2], "Y": [3, 4]})
        assert r.add_chart(df) is r

    def test_add_subtitle_returns_self(self) -> None:
        r = Report().add_sheet("S")
        assert r.add_subtitle("Sub") is r

    def test_add_paragraph_returns_self(self) -> None:
        r = Report().add_sheet("S")
        assert r.add_paragraph("text") is r

    def test_build_returns_bytes_when_no_path(self) -> None:
        r = Report(theme="business_blue")
        r.add_sheet("Data")
        r.add_title("Test")
        r.add_table(pd.DataFrame({"A": [1, 2, 3]}))
        result = r.build()
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_build_writes_file_when_path_given(self, temp_xlsx_path: Path) -> None:
        r = Report(theme="business_blue")
        r.add_sheet("Data")
        r.add_title("Report")
        r.add_table(pd.DataFrame({"X": [10, 20]}))
        result = r.build(temp_xlsx_path)
        assert result is None
        assert temp_xlsx_path.exists()
        assert temp_xlsx_path.stat().st_size > 0

    def test_build_multi_sheet(self, temp_xlsx_path: Path) -> None:
        r = Report(title="Multi-Sheet Report", theme="fresh_green")
        r.add_sheet("Sheet1")
        r.add_title("First Sheet")
        r.add_table(pd.DataFrame({"A": [1]}))

        r.add_sheet("Sheet2")
        r.add_title("Second Sheet")
        r.add_table(pd.DataFrame({"B": [2, 3]}))

        r.build(temp_xlsx_path)

        import openpyxl

        wb = openpyxl.load_workbook(temp_xlsx_path)
        assert "Sheet1" in wb.sheetnames
        assert "Sheet2" in wb.sheetnames

    def test_build_with_chart(self, temp_xlsx_path: Path) -> None:
        r = Report(theme="business_blue")
        r.add_sheet("Chart")
        r.add_title("Sales")
        r.add_chart(
            pd.DataFrame({"Month": ["Jan", "Feb", "Mar"], "Revenue": [100, 200, 150]}),
            type="column",
            category_col="Month",
            value_cols=["Revenue"],
            title="Revenue by Month",
        )
        r.build(temp_xlsx_path)
        assert temp_xlsx_path.stat().st_size > 0

    def test_build_full_report(self, temp_xlsx_path: Path) -> None:
        """Integration: build a full multi-element report."""
        r = Report(title="Q3 Analysis", theme="business_blue")
        r.add_sheet("Analysis")
        r.add_title("Q3 2026 Sales Analysis")
        r.add_subtitle("Executive Summary")
        r.add_paragraph(
            "This report provides an overview of Q3 2026 sales performance across all regions."
        )
        r.add_table(
            pd.DataFrame(
                {
                    "Region": ["North", "South", "East", "West"],
                    "Revenue": [125000, 98000, 142000, 87000],
                    "Growth": [0.12, 0.08, 0.15, 0.05],
                }
            ),
            title="Regional Performance",
        )
        r.add_chart(
            pd.DataFrame(
                {
                    "Month": ["Jul", "Aug", "Sep"],
                    "Revenue": [42000, 45000, 48000],
                }
            ),
            type="line",
            category_col="Month",
            value_cols=["Revenue"],
            title="Monthly Revenue Trend",
        )
        r.build(temp_xlsx_path)
        assert temp_xlsx_path.stat().st_size > 0

    def test_build_minimal(self) -> None:
        """Build with minimal configuration."""
        r = Report()
        r.add_sheet("Data")
        r.add_table(pd.DataFrame({"X": [1]}))
        data = r.build()
        assert isinstance(data, bytes)

    def test_apply_template_simple(self, temp_xlsx_path: Path) -> None:
        r = Report(theme="business_blue")
        df = pd.DataFrame({"A": [1, 2, 3]})
        r.apply_template("simple", title="Simple", table_df=df)
        r.build(temp_xlsx_path)
        assert temp_xlsx_path.exists()

    def test_apply_template_invalid_raises(self) -> None:
        r = Report()
        with pytest.raises(ValueError, match="not found"):
            r.apply_template("nonexistent")
