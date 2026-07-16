"""Image element — inserts external images into reports."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from databloom.core.grid import ElementPlacement
from databloom.elements.base import BaseElement
from databloom.settings import settings
from databloom.theme.base import Theme

if TYPE_CHECKING:
    pass


class ImageElement(BaseElement):
    """Inserts an image (PNG, JPG, etc.) from a file path or bytes buffer.

    The element measures itself based on the ``width_hint`` and
    ``height_hint`` because xlsxwriter image dimensions are set at
    insertion time.

    Example::

        el = ImageElement("charts/sales_map.png", height_hint=15)
        el.render(wm, sheet, placement, theme)
    """

    def __init__(
        self,
        image_path: str | Path,
        *,
        scale_x: float | None = None,
        scale_y: float | None = None,
        height_hint: int = 0,
        width_hint: int = 0,
    ) -> None:
        """Initialize the image element.

        Args:
            image_path: Path to a PNG, JPG, or other image file.
            scale_x: Horizontal scale factor (1.0 = original).
            scale_y: Vertical scale factor (1.0 = original).
            height_hint: Override row count.
            width_hint: Override column count.
        """
        super().__init__(height_hint=height_hint, width_hint=width_hint)
        self.image_path = Path(image_path)
        self.scale_x = scale_x if scale_x is not None else settings.image.default_scale_x
        self.scale_y = scale_y if scale_y is not None else settings.image.default_scale_y

    def measure(self, theme: Theme) -> tuple[int, int]:
        rows = self.height_hint or settings.image.default_height_rows
        cols = self.width_hint or settings.image.default_width_cols
        return (rows, cols)

    def render(
        self,
        workbook: object,
        sheet: object,
        placement: ElementPlacement,
        theme: Theme,
    ) -> None:
        options: dict = {
            "x_scale": self.scale_x,
            "y_scale": self.scale_y,
        }
        sheet.insert_image(  # type: ignore[union-attr]
            placement.start_row,
            placement.start_col,
            str(self.image_path),
            options,
        )

    def needs_full_width(self) -> bool:
        return False
