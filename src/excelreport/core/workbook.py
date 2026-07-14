"""Workbook and worksheet management for excelreport.

Provides a thin, ergonomic wrapper around xlsxwriter's Workbook and
worksheet classes. Handles lifecycle (create, close), format caching,
and coordinate conversion.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from xlsxwriter.format import Format
    from xlsxwriter.workbook import Workbook
    from xlsxwriter.worksheet import Worksheet


class FormatCache:
    """Cache for xlsxwriter Format objects to avoid duplicate creation.

    xlsxwriter has a limit of ~64,000 unique formats per workbook.
    This cache ensures identical format specs reuse the same Format object.
    """

    def __init__(self) -> None:
        self._cache: dict[tuple, Format] = {}

    def get(self, workbook: Workbook, **kwargs: object) -> Format:
        """Get or create a Format with the given properties.

        Args:
            workbook: The xlsxwriter Workbook the format belongs to.
            **kwargs: Format properties (bold=, font_name=, bg_color=, etc.).

        Returns:
            A cached or newly created Format object.
        """
        # Sort for stable cache keys
        key = tuple(sorted((str(k), str(v)) for k, v in kwargs.items() if v is not None))
        if key not in self._cache:
            fmt = workbook.add_format(kwargs)  # type: ignore[arg-type]
            self._cache[key] = fmt
        return self._cache[key]


class WorkbookManager:
    """Manages an xlsxwriter Workbook and its worksheets.

    Wraps the raw xlsxwriter API to provide:
    - Unified workbook creation (file path or in-memory bytes)
    - Sheet lookup and creation
    - Format caching via a shared ``FormatCache``
    - Proper cleanup via ``close()``

    Example::

        with WorkbookManager(path) as wm:
            ws = wm.add_sheet("Overview")
            fmt = wm.format_cache.get(wm.wb, bold=True, font_size=14)
            ws.write(0, 0, "Hello", fmt)
    """

    def __init__(self, output: str | Path | None = None) -> None:
        """Initialize the manager.

        Args:
            output: File path to write to. If ``None``, writes to an
                in-memory ``io.BytesIO`` buffer (use ``close()`` to
                retrieve the bytes).
        """
        self._output = Path(output) if output else None
        self._buffer: io.BytesIO | None = None
        if self._output:
            self._output.parent.mkdir(parents=True, exist_ok=True)
            self.wb: Workbook = __import__("xlsxwriter").Workbook(
                str(self._output),
                {"constant_memory": False},
            )
        else:
            self._buffer = io.BytesIO()
            self.wb: Workbook = __import__("xlsxwriter").Workbook(
                self._buffer,
                {"constant_memory": False, "in_memory": True},
            )
        self.format_cache = FormatCache()
        self._sheets: dict[str, Worksheet] = {}
        self._closed = False

    def add_sheet(self, name: str) -> Worksheet:
        """Add a new worksheet or return an existing one.

        Args:
            name: Sheet name (31-char limit enforced by xlsxwriter).

        Returns:
            The new or existing worksheet.

        Raises:
            ValueError: If the name is already taken (duplicate detection).
        """
        if name in self._sheets:
            raise ValueError(f"Sheet {name!r} already exists in this workbook")
        ws = self.wb.add_worksheet(name)
        self._sheets[name] = ws
        return ws

    def get_sheet(self, name: str) -> Worksheet:
        """Get an existing worksheet by name.

        Args:
            name: Exact sheet name.

        Returns:
            The worksheet.

        Raises:
            KeyError: If no sheet with that name exists.
        """
        if name not in self._sheets:
            raise KeyError(f"Sheet {name!r} not found. Available: {list(self._sheets)}")
        return self._sheets[name]

    def has_sheet(self, name: str) -> bool:
        """Check if a sheet name exists."""
        return name in self._sheets

    @property
    def sheet_count(self) -> int:
        """Number of sheets in the workbook."""
        return len(self._sheets)

    def close(self) -> bytes | None:
        """Close the workbook.

        Returns:
            The file bytes if the workbook was writing to memory
            (output was ``None``), otherwise ``None``.
        """
        if self._closed:
            return None
        self._closed = True
        self.wb.close()
        if self._buffer is not None:
            data = self._buffer.getvalue()
            self._buffer.close()
            return data
        return None

    def __enter__(self) -> WorkbookManager:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
