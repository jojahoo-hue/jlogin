"""RGB renderer - Family 1 (color works like the misty forest, wind turbines).

You supply three channel functions R, G, B mapping the (X, Y) grids to a raw
float field. Each is pushed through an `intensity` map (default: Yeganeh's F)
and assembled into a uint8 image.

  - Faithful reproductions: keep intensity=F (channels are tuned to it).
  - Original direct-color works: pass intensity=clip255 and return 0..255.
"""

from __future__ import annotations

from typing import Callable
import numpy as np
from PIL import Image

from ..canvas import Canvas
from ..intensity import F

ChannelFn = Callable[[np.ndarray, np.ndarray], np.ndarray]
Intensity = Callable[[np.ndarray], np.ndarray]


def clip255(x: np.ndarray) -> np.ndarray:
    """Passthrough intensity for channels already expressed in 0..255."""
    return np.clip(np.asarray(x, dtype=np.float64), 0.0, 255.0)


def render_rgb(
    canvas: Canvas,
    R: ChannelFn,
    G: ChannelFn,
    B: ChannelFn,
    intensity: Intensity = F,
) -> Image.Image:
    X, Y = canvas.grid()
    r = intensity(R(X, Y))
    g = intensity(G(X, Y))
    b = intensity(B(X, Y))
    img = np.stack([r, g, b], axis=-1).astype(np.uint8)
    return Image.fromarray(img, mode="RGB")
