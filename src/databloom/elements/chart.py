"""Chart element — renders charts using xlsxwriter native charts and matplotlib."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import numpy as np
import pandas as pd

from databloom.core.grid import ElementPlacement
from databloom.elements.base import BaseElement
from databloom.settings import settings
from databloom.theme.base import Theme

if TYPE_CHECKING:
    pass

ChartType = Literal["column", "bar", "line", "pie", "area", "scatter", "doughnut", "radar", "stock"]


def _chart_category_col(df: pd.DataFrame) -> str:
    """Guess the best category (X-axis) column from a DataFrame."""
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return str(col)
        if pd.api.types.is_string_dtype(df[col]):
            return str(col)
        if pd.api.types.is_categorical_dtype(df[col]):
            return str(col)
    # Fallback: first column
    return str(df.columns[0])


def _numeric_cols(df: pd.DataFrame, category_col: str) -> list[str]:
    """Return all numeric column names except the category column."""
    return [
        str(c)
        for c in df.columns
        if str(c) != category_col and pd.api.types.is_numeric_dtype(df[c])
    ] or [str(c) for c in df.columns if str(c) != category_col]


class ChartElement(BaseElement):
    """Renders a chart from a pandas DataFrame.

    Supports two backends:
    - ``"xlsxwriter"`` (default): Native Excel chart — interactive,
      editable in Excel, but less visually polished.
    - ``"matplotlib"``: Renders chart as a static image and inserts it.
      More visually flexible (custom annotations, color gradients, etc.)
      but not interactive.

    Example::

        el = ChartElement(trend_df, chart_type="line",
                          category_col="Date", title="Sales Trend")
        el.render(wm, sheet, placement, theme)
    """

    _chart_counter: int = 0  # class-level counter for hidden data sheets

    chart_types: dict[str, str] = {
        "column": "column",
        "bar": "bar",
        "line": "line",
        "pie": "pie",
        "doughnut": "doughnut",
        "area": "area",
        "scatter": "scatter",
        "radar": "radar",
        "stock": "stock",
    }

    def __init__(
        self,
        dataframe: pd.DataFrame,
        chart_type: ChartType = "column",
        *,
        category_col: str | None = None,
        value_cols: list[str] | None = None,
        title: str = "",
        backend: Literal["xlsxwriter", "matplotlib"] = "xlsxwriter",
        height_hint: int = 0,
        width_hint: int = 0,
        chart_width: int | None = None,
        chart_height: int | None = None,
        full_width: bool = True,
    ) -> None:
        """Initialize the chart element.

        Args:
            dataframe: Source data. Should have at least one category column
                and one or more numeric columns.
            chart_type: Chart type.
            category_col: Which column to use as the X axis / categories.
                Auto-detected if omitted.
            value_cols: Which columns to plot as series.
                Defaults to all numeric columns except the category.
            title: Chart title text.
            backend: Rendering backend.
            height_hint: Override row count.
            width_hint: Override column count.
            chart_width: Chart width in pixels.
            chart_height: Chart height in pixels.
            full_width: Whether the chart should span the full sheet width
                (default True). Set to False for dashboard-style side-by-side
                chart layouts.
        """
        super().__init__(height_hint=height_hint, width_hint=width_hint)
        self.dataframe = dataframe
        self.chart_type = chart_type
        self.category_col = category_col or _chart_category_col(dataframe)
        self.value_cols = value_cols or _numeric_cols(dataframe, self.category_col)
        self.title = title
        self.backend = backend
        self.chart_width = chart_width if chart_width is not None else settings.chart.default_width
        self.chart_height = chart_height if chart_height is not None else settings.chart.default_height
        self._full_width = full_width

    def measure(self, theme: Theme) -> tuple[int, int]:
        rows = max(self.height_hint, int(self.chart_height / settings.chart.rows_per_unit))
        cols = max(self.width_hint, int(self.chart_width / settings.chart.cols_per_unit))
        return (rows, cols)

    def render(
        self,
        workbook: object,
        sheet: object,
        placement: ElementPlacement,
        theme: Theme,
    ) -> None:
        if self.backend == "matplotlib":
            self._render_matplotlib(workbook, sheet, placement, theme)
        else:
            self._render_xlsxwriter(workbook, sheet, placement, theme)

    def _render_xlsxwriter(
        self,
        workbook: object,
        sheet: object,
        placement: ElementPlacement,
        theme: Theme,
    ) -> None:
        """Render using xlsxwriter's native chart engine."""
        wb = workbook.wb

        chart = wb.add_chart({"type": self.chart_type})
        chart.set_size({"width": self.chart_width, "height": self.chart_height})

        if self.title:
            chart.set_title({"name": self.title})

        # Set series colors from theme
        chart_colors = theme.all_chart_colors

        # ── Doughnut chart ────────────────────────────────────────
        if self.chart_type == "doughnut":
            chart.set_hole_size(40)  # 40% hole = donut feel

        # Write a hidden data table for the chart
        ChartElement._chart_counter += 1
        hidden_name = f"_databloom_chartdata_{ChartElement._chart_counter}"
        try:
            if hasattr(workbook, "add_sheet"):
                data_sheet = workbook.add_sheet(hidden_name)
                data_sheet.hide()  # type: ignore[union-attr]
            else:
                data_sheet = workbook.wb.add_worksheet(hidden_name)
                data_sheet.hide()
            data_start_row = 0
            data_start_col = 0
        except ValueError:
            # sheet already exists — use a unique suffix
            import random

            hidden_name = (
                f"_databloom_chartdata_{ChartElement._chart_counter}_{random.randint(0, 9999)}"
            )
            if hasattr(workbook, "add_sheet"):
                data_sheet = workbook.add_sheet(hidden_name)
                data_sheet.hide()  # type: ignore[union-attr]
            else:
                data_sheet = workbook.wb.add_worksheet(hidden_name)
                data_sheet.hide()
            data_start_row = 0
            data_start_col = 0

        df = self.dataframe
        cat_col = self.category_col

        # Write headers
        data_sheet.write(data_start_row, data_start_col, str(cat_col))  # type: ignore[union-attr]
        for vi, vc in enumerate(self.value_cols):
            data_sheet.write(data_start_row, data_start_col + 1 + vi, vc)  # type: ignore[union-attr]

        # Write data
        for ri in range(len(df)):
            row_data = df.iloc[ri]
            data_sheet.write(data_start_row + 1 + ri, data_start_col, str(row_data[cat_col]))  # type: ignore[union-attr]
            for vi, vc in enumerate(self.value_cols):
                data_sheet.write(data_start_row + 1 + ri, data_start_col + 1 + vi, row_data[vc])  # type: ignore[union-attr]

        # Add series
        for vi, vc in enumerate(self.value_cols):
            color = chart_colors[vi % len(chart_colors)]
            series_data = {
                "name": vc,
                "categories": [
                    data_sheet.name,  # type: ignore[union-attr]
                    data_start_row + 1,
                    data_start_col,
                    data_start_row + len(df),
                    data_start_col,
                ],
                "values": [
                    data_sheet.name,  # type: ignore[union-attr]
                    data_start_row + 1,
                    data_start_col + 1 + vi,
                    data_start_row + len(df),
                    data_start_col + 1 + vi,
                ],
                "fill": {"color": color},
                "line": {"color": color},
            }

            # Pie charts need per-point colors, not per-series colors
            if self.chart_type == "pie":
                n_points = len(df)
                series_data["points"] = [
                    {"fill": {"color": chart_colors[i % len(chart_colors)]}}
                    for i in range(n_points)
                ]

            chart.add_series(series_data)

        sheet.insert_chart(  # type: ignore[union-attr]
            placement.start_row, placement.start_col, chart
        )

    def _render_matplotlib(
        self,
        workbook: object,
        sheet: object,
        placement: ElementPlacement,
        theme: Theme,
    ) -> None:
        """Render chart as a matplotlib image and insert into the sheet."""
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.ticker import FuncFormatter

        chart_colors = theme.all_chart_colors
        df = self.dataframe

        dpi = settings.chart.matplotlib_dpi
        figsize = (self.chart_width / dpi, self.chart_height / dpi)
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

        # Set style from theme
        ax.set_facecolor(settings.chart.axes_facecolor)
        fig.patch.set_facecolor(settings.chart.figure_facecolor)

        if self.title:
            ax.set_title(
                self.title,
                fontsize=settings.chart.title_fontsize,
                fontweight=settings.chart.title_fontweight,
                color=theme.title.font.color,
            )

        cat_labels = [str(v) for v in df[self.category_col]]

        for vi, vc in enumerate(self.value_cols):
            color = chart_colors[vi % len(chart_colors)]
            values = df[vc].values

            if self.chart_type == "column":
                x_pos = np.arange(len(df)) + vi * settings.chart.bar_group_offset
                ax.bar(
                    x_pos,
                    values,
                    settings.chart.bar_width_fraction,
                    label=vc,
                    color=color,
                    alpha=settings.chart.bar_alpha,
                )
                ax.set_xticks(
                    np.arange(len(df))
                    + settings.chart.bar_group_offset * (len(self.value_cols) - 1) / 2
                )
                ax.set_xticklabels(cat_labels, rotation=settings.chart.xtick_rotation, ha=settings.chart.xlabel_ha)
            elif self.chart_type == "bar":
                ax.barh(
                    np.arange(len(df)),
                    values,
                    color=color,
                    alpha=settings.chart.bar_alpha,
                    label=vc,
                )
                ax.set_yticks(np.arange(len(df)))
                ax.set_yticklabels(cat_labels)
            elif self.chart_type == "line":
                ax.plot(
                    cat_labels,
                    values,
                    marker="o",
                    color=color,
                    linewidth=settings.chart.linewidth,
                    markersize=settings.chart.markersize,
                    label=vc,
                )
                ax.tick_params(axis="x", rotation=settings.chart.xtick_rotation)
            elif self.chart_type == "pie":
                ax.pie(
                    values,
                    labels=cat_labels,
                    autopct=settings.chart.pie_autopct,
                    colors=chart_colors[: len(df)],
                    startangle=settings.chart.pie_startangle,
                )
                ax.axis("equal")
                break  # only one series for pie
            elif self.chart_type == "area":
                ax.fill_between(
                    range(len(df)), values, alpha=settings.chart.area_alpha, color=color
                )
                ax.plot(range(len(df)), values, color=color, linewidth=settings.chart.linewidth, label=vc)
                ax.set_xticks(range(len(df)))
                ax.set_xticklabels(cat_labels, rotation=settings.chart.xtick_rotation, ha=settings.chart.xlabel_ha)
            elif self.chart_type == "scatter":
                ax.scatter(
                    range(len(df)),
                    values,
                    color=color,
                    s=settings.chart.scatter_size,
                    label=vc,
                    alpha=settings.chart.scatter_alpha,
                )
            elif self.chart_type == "doughnut":
                wedges, texts, autotexts = ax.pie(
                    values,
                    labels=cat_labels,
                    autopct=settings.chart.pie_autopct,
                    colors=chart_colors[: len(df)],
                    startangle=settings.chart.pie_startangle,
                    wedgeprops={"width": 0.4},  # 40% inner width = donut
                )
                ax.axis("equal")
                break  # only one series for doughnut
            elif self.chart_type == "radar":
                # Radar chart needs at least 3 points to form a polygon
                angles = np.linspace(0, 2 * np.pi, len(cat_labels), endpoint=False).tolist()
                angles += angles[:1]  # close the polygon
                values_radar = list(values) + [list(values)[0]]
                ax.fill(angles, values_radar, alpha=0.25, color=color)
                ax.plot(angles, values_radar, "o-", linewidth=settings.chart.linewidth, color=color, label=vc)
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(cat_labels)
            elif self.chart_type == "stock":
                # Stock chart: expects OHLC data in first 4 value columns
                stock_values = values  # single series for stock (uses first value col)
                ax.plot(cat_labels, stock_values, "o-", color=color,
                        linewidth=settings.chart.linewidth, markersize=settings.chart.markersize, label=vc)
                ax.tick_params(axis="x", rotation=settings.chart.xtick_rotation)
                # Fill between alternating regions for up/down visualization
                for i in range(len(df) - 1):
                    if stock_values[i + 1] >= stock_values[i]:
                        ax.axvspan(i - 0.5, i + 0.5, alpha=0.1, color="#00AA00")
                    else:
                        ax.axvspan(i - 0.5, i + 0.5, alpha=0.1, color="#AA0000")

        if self.chart_type not in ("pie", "doughnut") and len(self.value_cols) > 1:
            ax.legend(
                loc=settings.chart.legend_location,
                framealpha=settings.chart.legend_framealpha,
            )

        # Format Y axis (skip for radar/polar charts)
        if self.chart_type != "radar":
            ax.yaxis.set_major_formatter(
                FuncFormatter(lambda x, _: settings.chart.yaxis_number_format.format(x=x))
            )

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(labelsize=settings.chart.tick_labelsize)
        plt.tight_layout()

        # Save to temp file in the same directory as the output (or a safe location)
        with tempfile.NamedTemporaryFile(
            suffix=settings.chart.temp_file_suffix, delete=False
        ) as tf:
            fig.savefig(
                tf,
                dpi=dpi,
                bbox_inches=settings.chart.savefig_bbox_inches,
                facecolor=settings.chart.savefig_facecolor,
            )
            tmp_path = tf.name
        plt.close(fig)

        # Keep a reference — xlsxwriter reads the file lazily on close()
        try:
            sheet.insert_image(  # type: ignore[union-attr]
                placement.start_row,
                placement.start_col,
                tmp_path,
                {
                    "x_scale": settings.chart.x_scale_factor,
                    "y_scale": settings.chart.y_scale_factor,
                },
            )
            # Add to deferred cleanup so the file exists until workbook is closed
            if not hasattr(workbook, "_chart_temp_files"):
                workbook._chart_temp_files = []  # type: ignore[attr-defined]
            workbook._chart_temp_files.append(tmp_path)  # type: ignore[attr-defined]
        except Exception:
            Path(tmp_path).unlink(missing_ok=True)
            raise

    def needs_full_width(self) -> bool:
        return self._full_width


class ComboChartElement(BaseElement):
    """Renders a combination chart with bars + line on dual Y-axes.

    The most common business chart pattern: columns/bars for volume
    metrics on the left axis, and a line for a rate/ratio metric
    on the right axis.

    Only the xlsxwriter backend is supported (matplotlib not implemented).

    Example::

        el = ComboChartElement(
            df,
            category_col="Month",
            bar_cols=["Revenue", "Cost"],
            line_cols=["Margin%"],
            bar_title="Revenue & Cost (¥)",
            line_title="Margin (%)",
            title="Monthly Revenue vs Margin",
        )
        el.render(wm, sheet, placement, theme)
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        *,
        category_col: str | None = None,
        bar_cols: list[str] | None = None,
        line_cols: list[str] | None = None,
        bar_title: str = "",
        line_title: str = "",
        title: str = "",
        height_hint: int = 0,
        width_hint: int = 0,
        chart_width: int | None = None,
        chart_height: int | None = None,
        full_width: bool = True,
    ) -> None:
        """Initialize the combo chart element.

        Args:
            dataframe: Source data with category + bar columns + line columns.
            category_col: X-axis column name (auto-detected if omitted).
            bar_cols: Column names rendered as bars/columns (left Y-axis).
            line_cols: Column names rendered as a line (right Y-axis).
            bar_title: Title for the bar group (left axis label).
            line_title: Title for the line (right axis label).
            title: Overall chart title.
            height_hint/width_hint: Layout overrides.
            chart_width/chart_height: Chart dimensions in pixels.
            full_width: Whether the chart spans full sheet width.
        """
        super().__init__(height_hint=height_hint, width_hint=width_hint)
        self.dataframe = dataframe
        self.category_col = category_col or _chart_category_col(dataframe)
        self.bar_cols = bar_cols or _numeric_cols(dataframe, self.category_col)
        self.line_cols = line_cols or []
        self.bar_title = bar_title
        self.line_title = line_title
        self.title = title
        self.chart_width = chart_width if chart_width is not None else settings.chart.default_width
        self.chart_height = chart_height if chart_height is not None else settings.chart.default_height
        self._full_width = full_width

    def measure(self, theme: Theme) -> tuple[int, int]:
        rows = max(self.height_hint, int(self.chart_height / settings.chart.rows_per_unit))
        cols = max(self.width_hint, int(self.chart_width / settings.chart.cols_per_unit))
        return (rows, cols)

    def render(
        self,
        workbook: object,
        sheet: object,
        placement: ElementPlacement,
        theme: Theme,
    ) -> None:
        """Render using xlsxwriter's chart.combine() for dual Y-axes."""
        wb = workbook.wb
        chart_colors = theme.all_chart_colors

        # Create hidden data sheet
        ChartElement._chart_counter += 1
        hidden_name = f"_databloom_chartdata_{ChartElement._chart_counter}"
        try:
            if hasattr(workbook, "add_sheet"):
                data_sheet = workbook.add_sheet(hidden_name)
                data_sheet.hide()
            else:
                data_sheet = workbook.wb.add_worksheet(hidden_name)
                data_sheet.hide()
            data_start_row = 0
            data_start_col = 0
        except ValueError:
            import random

            hidden_name = (
                f"_databloom_chartdata_{ChartElement._chart_counter}_{random.randint(0, 9999)}"
            )
            if hasattr(workbook, "add_sheet"):
                data_sheet = workbook.add_sheet(hidden_name)
                data_sheet.hide()
            else:
                data_sheet = workbook.wb.add_worksheet(hidden_name)
                data_sheet.hide()
            data_start_row = 0
            data_start_col = 0

        df = self.dataframe
        cat_col = self.category_col

        # Write headers
        all_cols = [cat_col] + self.bar_cols + self.line_cols
        for ci, col_name in enumerate(all_cols):
            data_sheet.write(data_start_row, data_start_col + ci, str(col_name))

        # Write data rows
        for ri in range(len(df)):
            row_data = df.iloc[ri]
            for ci, col_name in enumerate(all_cols):
                val = row_data[col_name]
                data_sheet.write(data_start_row + 1 + ri, data_start_col + ci, val)

        # Create bar chart (primary axis)
        bar_chart = wb.add_chart({"type": "column"})
        if self.title:
            bar_chart.set_title({"name": self.title})
        bar_chart.set_size({"width": self.chart_width, "height": self.chart_height})

        # Categories
        cat_range = [
            data_sheet.name,
            data_start_row + 1,
            data_start_col,
            data_start_row + len(df),
            data_start_col,
        ]

        for vi, vc in enumerate(self.bar_cols):
            color = chart_colors[vi % len(chart_colors)]
            bar_chart.add_series(
                {
                    "name": vc,
                    "categories": cat_range,
                    "values": [
                        data_sheet.name,
                        data_start_row + 1,
                        data_start_col + 1 + vi,
                        data_start_row + len(df),
                        data_start_col + 1 + vi,
                    ],
                    "fill": {"color": color},
                    "line": {"color": color},
                    "gap": settings.chart.combo_bar_gap,
                }
            )

        # Create line chart (secondary axis) and combine
        if self.line_cols:
            line_chart = wb.add_chart({"type": "line"})
            for vi, vc in enumerate(self.line_cols):
                color = chart_colors[(len(self.bar_cols) + vi) % len(chart_colors)]
                line_chart.add_series(
                    {
                        "name": vc,
                        "categories": cat_range,
                        "values": [
                            data_sheet.name,
                            data_start_row + 1,
                            data_start_col + 1 + len(self.bar_cols) + vi,
                            data_start_row + len(df),
                            data_start_col + 1 + len(self.bar_cols) + vi,
                        ],
                        "y2_axis": True,
                        "line": {
                            "color": color,
                            "width": settings.chart.combo_line_width,
                        },
                        "marker": {
                            "type": settings.chart.combo_line_marker_type,
                            "size": settings.chart.combo_line_marker_size,
                            "fill": {"color": color},
                        },
                    }
                )

            bar_chart.combine(line_chart)

        if self.bar_title:
            bar_chart.y_axis["name"] = self.bar_title
        if self.line_title:
            bar_chart.y2_axis["name"] = self.line_title

        sheet.insert_chart(placement.start_row, placement.start_col, bar_chart)

    def needs_full_width(self) -> bool:
        return self._full_width
