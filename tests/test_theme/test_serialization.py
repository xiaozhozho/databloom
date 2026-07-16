"""Tests for theme serialization."""

from __future__ import annotations

from databloom.theme.base import Theme
from databloom.theme.presets import (
    THEME_BUSINESS_BLUE,
    THEME_FINANCE_CHARCOAL,
    THEME_MEDICAL_TEAL,
)


class TestThemeSerialization:
    """Test Theme.to_dict() and Theme.from_dict() round-trips."""

    def test_to_dict_has_expected_keys(self) -> None:
        d = THEME_BUSINESS_BLUE.to_dict()
        expected = [
            "name",
            "global_font_name",
            "table",
            "title",
            "subtitle",
            "paragraph",
            "chart_colors",
            "accent_color",
            "sheet_margin_rows",
            "sheet_margin_cols",
            "element_spacing_rows",
        ]
        for key in expected:
            assert key in d, f"Missing key: {key}"

    def test_round_trip_business_blue(self) -> None:
        d = THEME_BUSINESS_BLUE.to_dict()
        t = Theme.from_dict(d)
        assert t.name == THEME_BUSINESS_BLUE.name
        assert t.global_font_name == THEME_BUSINESS_BLUE.global_font_name
        assert t.accent_color == THEME_BUSINESS_BLUE.accent_color
        assert t.chart_colors == THEME_BUSINESS_BLUE.chart_colors
        assert t.table.header_font.color == THEME_BUSINESS_BLUE.table.header_font.color

    def test_round_trip_finance_charcoal(self) -> None:
        d = THEME_FINANCE_CHARCOAL.to_dict()
        t = Theme.from_dict(d)
        assert t.name == "finance_charcoal"
        assert t.global_font_name == "Lato"
        assert t.table.header_fill.color == "#374151"

    def test_round_trip_medical_teal(self) -> None:
        d = THEME_MEDICAL_TEAL.to_dict()
        t = Theme.from_dict(d)
        assert t.name == "medical_teal"
        assert t.table.header_fill.color == "#0D9488"

    def test_from_dict_minimal(self) -> None:
        t = Theme.from_dict({"name": "minimal"})
        assert t.name == "minimal"
        assert t.global_font_name == "Arial"
        assert len(t.chart_colors) >= 1

    def test_to_dict_is_json_serializable(self) -> None:
        import json

        d = THEME_BUSINESS_BLUE.to_dict()
        s = json.dumps(d)
        assert isinstance(s, str)
        assert "business_blue" in s
