"""Inequality renderer - Family 2 (set works like the running horse).

The image is the set {(x, y) | T(x, y) > 0}. You supply a single field function
T; pixels where T > 0 are inked, the rest stay background.
"""

from __future__ import annotations

from typing import Callable
import numpy as np
from PIL import Image

from ..canvas import Canvas

FieldFn = Callable[[np.ndarray, np.ndarray], np.ndarray]


def render_set(
    canvas: Canvas,
    T: FieldFn,
    ink=(0, 0, 0),
    background=(255, 255, 255),
) -> Image.Image:
    X, Y = canvas.grid()
    mask = T(X, Y) > 0
    img = np.empty((canvas.height, canvas.width, 3), dtype=np.uint8)
    img[...] = background
    img[mask] = ink
    return Image.fromarray(img, mode="RGB")
