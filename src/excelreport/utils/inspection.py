"""DataFrame inspection utilities for smart report generation.

Detects column types, distribution characteristics, and suggests
appropriate chart types and report layouts based on data shape.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class ColumnInfo:
    """Metadata about a single DataFrame column."""

    name: str
    dtype_name: str
    is_numeric: bool = False
    is_temporal: bool = False
    is_categorical: bool = False
    is_text: bool = False
    is_boolean: bool = False
    unique_count: int = 0
    null_count: int = 0
    min_value: float | None = None
    max_value: float | None = None
    suggested_chart_role: str = ""  # "category", "value", "ignore"


@dataclass
class DataFrameProfile:
    """Summary profile of a DataFrame for smart report generation."""

    row_count: int = 0
    col_count: int = 0
    columns: list[ColumnInfo] = field(default_factory=list)
    numeric_cols: list[str] = field(default_factory=list)
    temporal_cols: list[str] = field(default_factory=list)
    categorical_cols: list[str] = field(default_factory=list)
    text_cols: list[str] = field(default_factory=list)
    boolean_cols: list[str] = field(default_factory=list)
    suggested_chart_types: list[str] = field(default_factory=list)
    suggested_layout: str = "simple"


def profile_dataframe(df: pd.DataFrame) -> DataFrameProfile:
    """Analyze a DataFrame and produce a structured profile.

    The profile includes per-column metadata (type, unique values, nulls,
    numeric range) and aggregated suggestions for chart types and layout.

    Args:
        df: Input DataFrame.

    Returns:
        A ``DataFrameProfile`` with complete analysis results.
    """
    profile = DataFrameProfile(
        row_count=len(df),
        col_count=len(df.columns),
    )

    for col_name in df.columns:
        series = df[col_name]
        col_info = ColumnInfo(
            name=str(col_name),
            dtype_name=str(series.dtype),
        )

        # Type detection
        if pd.api.types.is_numeric_dtype(series):
            col_info.is_numeric = True
            col_info.suggested_chart_role = "value"
            profile.numeric_cols.append(str(col_name))
            col_info.min_value = float(series.min()) if not series.isna().all() else None
            col_info.max_value = float(series.max()) if not series.isna().all() else None
        elif pd.api.types.is_datetime64_any_dtype(series):
            col_info.is_temporal = True
            col_info.suggested_chart_role = "category"
            profile.temporal_cols.append(str(col_name))
        elif pd.api.types.is_bool_dtype(series):
            col_info.is_boolean = True
            col_info.suggested_chart_role = "ignore"
            profile.boolean_cols.append(str(col_name))
        elif pd.api.types.is_string_dtype(series) or pd.api.types.is_categorical_dtype(series):
            unique = series.nunique()
            col_info.unique_count = int(unique)
            if unique <= 15 and unique < len(df) * 0.5:
                col_info.is_categorical = True
                col_info.suggested_chart_role = "category"
                profile.categorical_cols.append(str(col_name))
            else:
                col_info.is_text = True
                col_info.suggested_chart_role = "ignore"
                profile.text_cols.append(str(col_name))
        else:
            col_info.is_text = True
            col_info.suggested_chart_role = "ignore"
            profile.text_cols.append(str(col_name))

        col_info.null_count = int(series.isna().sum())
        profile.columns.append(col_info)

    # Suggest chart types
    if len(profile.temporal_cols) >= 1 and len(profile.numeric_cols) >= 1:
        profile.suggested_chart_types = ["line", "column"]
    elif len(profile.categorical_cols) >= 1 and len(profile.numeric_cols) >= 1:
        profile.suggested_chart_types = ["column", "bar"]
    elif len(profile.numeric_cols) >= 2:
        profile.suggested_chart_types = ["column", "scatter"]

    # Suggest layout
    if profile.col_count <= 5 and profile.row_count <= 20:
        profile.suggested_layout = "simple"
    elif profile.col_count <= 8:
        profile.suggested_layout = "summary_detail"
    else:
        profile.suggested_layout = "report"

    return profile
