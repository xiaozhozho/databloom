"""Tests for built-in theme presets and registry."""

from __future__ import annotations

import pytest

from excelreport.theme.base import FontSpec, TableStyle, Theme, TitleStyle
from excelreport.theme.presets import (
    THEME_BUSINESS_BLUE,
    THEME_CLASSIC_WHITE,
    THEME_FRESH_GREEN,
    THEME_MINIMAL_GRAY,
    THEME_TECH_DARK,
    THEME_WARM_ORANGE,
    _THEME_REGISTRY,
    get_theme,
    list_themes,
)


class TestPresetIntegrity:
    """Verify every preset theme is structurally sound."""

    THEMES = [
        THEME_BUSINESS_BLUE,
        THEME_FRESH_GREEN,
        THEME_TECH_DARK,
        THEME_WARM_ORANGE,
        THEME_MINIMAL_GRAY,
        THEME_CLASSIC_WHITE,
    ]

    @pytest.mark.parametrize("theme", THEMES)
    def test_theme_has_name(self, theme: Theme) -> None:
        assert theme.name, f"Theme {theme} has an empty name"
        assert isinstance(theme.name, str)

    @pytest.mark.parametrize("theme", THEMES)
    def test_theme_has_font_name(self, theme: Theme) -> None:
        assert theme.global_font_name, f"Theme {theme.name} has no global font"

    @pytest.mark.parametrize("theme", THEMES)
    def test_theme_has_10_chart_colors(self, theme: Theme) -> None:
        assert len(theme.chart_colors) == 10, (
            f"Theme {theme.name} has {len(theme.chart_colors)} chart colors, expected 10"
        )

    @pytest.mark.parametrize("theme", THEMES)
    def test_chart_colors_are_valid_hex(self, theme: Theme) -> None:
        for c in theme.chart_colors:
            assert c.startswith("#"), f"Theme {theme.name}: {c!r} not hex"
            assert len(c) == 7, f"Theme {theme.name}: {c!r} wrong length"

    @pytest.mark.parametrize("theme", THEMES)
    def test_table_header_font_is_bold(self, theme: Theme) -> None:
        assert theme.table.header_font.bold is True, (
            f"Theme {theme.name}: header font not bold"
        )

    @pytest.mark.parametrize("theme", THEMES)
    def test_title_font_is_bold(self, theme: Theme) -> None:
        assert theme.title.font.bold is True, (
            f"Theme {theme.name}: title font not bold"
        )

    @pytest.mark.parametrize("theme", THEMES)
    def test_title_is_larger_than_subtitle(self, theme: Theme) -> None:
        assert theme.title.font.size > theme.subtitle.font.size, (
            f"Theme {theme.name}: title({theme.title.font.size}) <= subtitle({theme.subtitle.font.size})"
        )

    @pytest.mark.parametrize("theme", THEMES)
    def test_header_font_larger_than_data_font(self, theme: Theme) -> None:
        assert theme.table.header_font.size > theme.table.data_font.size, (
            f"Theme {theme.name}: header({theme.table.header_font.size}) <= data({theme.table.data_font.size})"
        )

    @pytest.mark.parametrize("theme", THEMES)
    def test_accent_color_is_hex(self, theme: Theme) -> None:
        assert theme.accent_color.startswith("#")
        assert len(theme.accent_color) == 7

    @pytest.mark.parametrize("theme", THEMES)
    def test_margins_are_positive(self, theme: Theme) -> None:
        assert theme.sheet_margin_rows >= 0
        assert theme.sheet_margin_cols >= 0
        assert theme.element_spacing_rows >= 0


class TestBusinessBlue:
    """Tests specific to the business_blue theme."""

    def test_header_is_dark_blue(self) -> None:
        assert THEME_BUSINESS_BLUE.table.header_fill.color == "#2F5496"

    def test_header_text_is_white(self) -> None:
        assert THEME_BUSINESS_BLUE.table.header_font.color == "#FFFFFF"

    def test_accent_matches_header(self) -> None:
        assert THEME_BUSINESS_BLUE.accent_color == "#2F5496"

    def test_title_color_darker_than_header(self) -> None:
        assert THEME_BUSINESS_BLUE.title.font.color == "#1F3864"


class TestFreshGreen:
    """Tests specific to the fresh_green theme."""

    def test_uses_calibri(self) -> None:
        assert THEME_FRESH_GREEN.global_font_name == "Calibri"

    def test_header_is_green(self) -> None:
        assert THEME_FRESH_GREEN.table.header_fill.color == "#548235"


class TestTechDark:
    """Tests specific to the tech_dark theme."""

    def test_dark_background(self) -> None:
        assert THEME_TECH_DARK.table.data_fill_odd.color != "#FFFFFF"

    def test_cyan_accent(self) -> None:
        assert THEME_TECH_DARK.accent_color == "#00BCD4"


class TestWarmOrange:
    """Tests specific to the warm_orange theme."""

    def test_uses_tahoma(self) -> None:
        assert THEME_WARM_ORANGE.global_font_name == "Tahoma"

    def test_header_is_orange(self) -> None:
        assert THEME_WARM_ORANGE.table.header_fill.color == "#ED7D31"


class TestMinimalGray:
    """Tests specific to the minimal_gray theme."""

    def test_low_contrast(self) -> None:
        assert THEME_MINIMAL_GRAY.table.data_border.color == "#E0E0E0"

    def test_uses_helvetica(self) -> None:
        assert THEME_MINIMAL_GRAY.global_font_name == "Helvetica"


class TestClassicWhite:
    """Tests specific to the classic_white theme."""

    def test_white_background(self) -> None:
        assert THEME_CLASSIC_WHITE.table.header_fill.color == "#FFFFFF"

    def test_no_alternating_rows(self) -> None:
        assert THEME_CLASSIC_WHITE.table.data_fill_odd == THEME_CLASSIC_WHITE.table.data_fill_even


class TestGetTheme:
    """Tests for get_theme registry function."""

    def test_get_existing_theme(self) -> None:
        t = get_theme("business_blue")
        assert t.name == "business_blue"
        assert t is THEME_BUSINESS_BLUE  # returns same instance

    def test_get_case_sensitive(self) -> None:
        with pytest.raises(KeyError, match="Business_Blue"):
            get_theme("Business_Blue")

    def test_get_missing_raises_keyerror(self) -> None:
        with pytest.raises(KeyError, match="not found"):
            get_theme("nonexistent_theme")

    @pytest.mark.parametrize("name", ["business_blue", "fresh_green", "tech_dark",
                                       "warm_orange", "minimal_gray", "classic_white"])
    def test_all_themes_retrievable(self, name: str) -> None:
        t = get_theme(name)
        assert isinstance(t, Theme)
        assert t.name == name


class TestListThemes:
    """Tests for list_themes."""

    def test_returns_six_themes(self) -> None:
        names = list_themes()
        assert len(names) == 6

    def test_returns_sorted(self) -> None:
        names = list_themes()
        assert names == sorted(names)

    def test_includes_business_blue(self) -> None:
        assert "business_blue" in list_themes()

    def test_includes_tech_dark(self) -> None:
        assert "tech_dark" in list_themes()


class TestThemeRegistry:
    """Tests for the internal registry."""

    def test_registry_has_six_entries(self) -> None:
        assert len(_THEME_REGISTRY) == 6

    def test_registry_keys_match_names(self) -> None:
        for key, theme in _THEME_REGISTRY.items():
            assert key == theme.name

    def test_all_names_are_lowercase(self) -> None:
        for name in _THEME_REGISTRY:
            assert name == name.lower()
