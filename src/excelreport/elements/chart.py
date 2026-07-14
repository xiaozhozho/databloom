"""Chart element — renders charts using xlsxwriter native charts and matplotlib."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import numpy as np
import pandas as pd

from excelreport.core.grid import ElementPlacement
from excelreport.elements.base import BaseElement
from excelreport.theme.base import Theme

if TYPE_CHECKING:
    pass

ChartType = Literal["column", "bar", "line", "pie", "area", "scatter"]


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

    chart_types: dict[str, str] = {
        "column": "column",
        "bar": "bar",
        "line": "line",
        "pie": "pie",
        "area": "area",
        "scatter": "scatter",
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
        chart_width: int = 640,
        chart_height: int = 400,
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
        """
        super().__init__(height_hint=height_hint, width_hint=width_hint)
        self.dataframe = dataframe
        self.chart_type = chart_type
        self.category_col = category_col or _chart_category_col(dataframe)
        self.value_cols = value_cols or _numeric_cols(dataframe, self.category_col)
        self.title = title
        self.backend = backend
        self.chart_width = chart_width
        self.chart_height = chart_height

    def measure(self, theme: Theme) -> tuple[int, int]:
        # Approx: 400px chart = ~20 Excel rows at default height
        rows = max(self.height_hint, int(self.chart_height / 20))
        cols = max(self.width_hint, int(self.chart_width / 60))
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

        # Write a hidden data table for the chart
        data_start_row = placement.start_row
        data_start_col = placement.start_col + placement.col_count + 2  # offset

        df = self.dataframe
        cat_col = self.category_col

        # Write headers
        sheet.write(data_start_row, data_start_col, str(cat_col))  # type: ignore[union-attr]
        for vi, vc in enumerate(self.value_cols):
            sheet.write(data_start_row, data_start_col + 1 + vi, vc)  # type: ignore[union-attr]

        # Write data
        for ri in range(len(df)):
            row_data = df.iloc[ri]
            sheet.write(data_start_row + 1 + ri, data_start_col, str(row_data[cat_col]))  # type: ignore[union-attr]
            for vi, vc in enumerate(self.value_cols):
                sheet.write(data_start_row + 1 + ri, data_start_col + 1 + vi, row_data[vc])  # type: ignore[union-attr]

        # Add series
        for vi, vc in enumerate(self.value_cols):
            color = chart_colors[vi % len(chart_colors)]
            chart.add_series(
                {
                    "name": vc,
                    "categories": [
                        sheet.name,  # type: ignore[union-attr]
                        data_start_row + 1,
                        data_start_col,
                        data_start_row + len(df),
                        data_start_col,
                    ],
                    "values": [
                        sheet.name,  # type: ignore[union-attr]
                        data_start_row + 1,
                        data_start_col + 1 + vi,
                        data_start_row + len(df),
                        data_start_col + 1 + vi,
                    ],
                    "fill": {"color": color},
                    "line": {"color": color},
                }
            )

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

        dpi = 100
        figsize = (self.chart_width / dpi, self.chart_height / dpi)
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

        # Set style from theme
        ax.set_facecolor("#FFFFFF")
        fig.patch.set_facecolor("#FFFFFF")

        if self.title:
            ax.set_title(self.title, fontsize=14, fontweight="bold", color=theme.title.font.color)

        cat_labels = [str(v) for v in df[self.category_col]]

        for vi, vc in enumerate(self.value_cols):
            color = chart_colors[vi % len(chart_colors)]
            values = df[vc].values

            if self.chart_type == "column":
                x_pos = np.arange(len(df)) + vi * 0.2
                ax.bar(x_pos, values, 0.2, label=vc, color=color, alpha=0.85)
                ax.set_xticks(np.arange(len(df)) + 0.2 * (len(self.value_cols) - 1) / 2)
                ax.set_xticklabels(cat_labels, rotation=45, ha="right")
            elif self.chart_type == "bar":
                ax.barh(np.arange(len(df)), values, color=color, alpha=0.85, label=vc)
                ax.set_yticks(np.arange(len(df)))
                ax.set_yticklabels(cat_labels)
            elif self.chart_type == "line":
                ax.plot(
                    cat_labels, values, marker="o", color=color, linewidth=2, markersize=4, label=vc
                )
                ax.tick_params(axis="x", rotation=45)
            elif self.chart_type == "pie":
                ax.pie(
                    values,
                    labels=cat_labels,
                    autopct="%1.1f%%",
                    colors=chart_colors[: len(df)],
                    startangle=90,
                )
                ax.axis("equal")
                break  # only one series for pie
            elif self.chart_type == "area":
                ax.fill_between(range(len(df)), values, alpha=0.3, color=color)
                ax.plot(range(len(df)), values, color=color, linewidth=2, label=vc)
                ax.set_xticks(range(len(df)))
                ax.set_xticklabels(cat_labels, rotation=45, ha="right")
            elif self.chart_type == "scatter":
                ax.scatter(range(len(df)), values, color=color, s=40, label=vc, alpha=0.8)

        if self.chart_type != "pie" and len(self.value_cols) > 1:
            ax.legend(loc="best", framealpha=0.8)

        # Format Y axis
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:,.0f}"))

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(labelsize=9)
        plt.tight_layout()

        # Save to temp file in the same directory as the output (or a safe location)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
            fig.savefig(tf, dpi=dpi, bbox_inches="tight", facecolor="white")
            tmp_path = tf.name
        plt.close(fig)

        # Keep a reference — xlsxwriter reads the file lazily on close()
        try:
            sheet.insert_image(  # type: ignore[union-attr]
                placement.start_row,
                placement.start_col,
                tmp_path,
                {
                    "x_scale": self.chart_width / (self.chart_width * 1.0),
                    "y_scale": self.chart_height / (self.chart_height * 1.0),
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
        return True
