"""Canvas: maps the pixel grid (m, n) onto mathematical coordinates (x, y).

In Yeganeh's works the pixel of row `n`, column `m` is colored by evaluating
functions at a *normalized* coordinate, e.g. for the misty forest
(a 2000x1200 image):

    x = (m - 1000) / 600
    y = (601 - n) / 600

`Canvas` builds the full vectorized (X, Y) numpy grids in one shot so a whole
image can be evaluated with array math instead of 2.4M Python-level calls.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class Canvas:
    width: int          # number of columns (m = 1..width)
    height: int         # number of rows    (n = 1..height)
    x0: float           # m offset:  x = (m - x0) / x_scale
    x_scale: float
    y0: float           # n offset:  y = (y0 - n) / y_scale
    y_scale: float

    @classmethod
    def yeganeh(cls, width: int, height: int, scale: float) -> "Canvas":
        """The mapping Yeganeh uses: x centered on width/2, y flipped.

        Reproduces e.g. forest(2000, 1200, 600) -> x=(m-1000)/600, y=(601-n)/600.
        """
        return cls(
            width=width,
            height=height,
            x0=width / 2,
            x_scale=scale,
            y0=height / 2 + 1,
            y_scale=scale,
        )

    def grid(self) -> tuple[np.ndarray, np.ndarray]:
        """Return (X, Y) arrays of shape (height, width)."""
        m = np.arange(1, self.width + 1, dtype=np.float64)
        n = np.arange(1, self.height + 1, dtype=np.float64)
        X = (m[None, :] - self.x0) / self.x_scale
        Y = (self.y0 - n[:, None]) / self.y_scale
        # broadcast to full grids
        X = np.broadcast_to(X, (self.height, self.width))
        Y = np.broadcast_to(Y, (self.height, self.width))
        return X, Y
