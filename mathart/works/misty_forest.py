"""Misty Forest - Family 1 (color), in the spirit of Yeganeh's forest.

Now uses the shapes library: shapes.fir for the trees, shapes.bird for the
flying bird (as in the original "Bird Flying Over a Misty Forest"), plus depth
fog. Original composition; swap R/G/B + intensity=F for a byte-exact repro.
"""

from __future__ import annotations

import numpy as np

from ..canvas import Canvas
from ..renderers import render_rgb, clip255
from .. import shapes as S

# back-to-front: (center_x, base_y, height, half_width, opacity, tint)
_TREES = [
    (-1.7, -1.0, 2.2, 0.55, 0.35, (95, 95, 130)),
    (1.6, -1.0, 2.4, 0.60, 0.38, (90, 92, 128)),
    (-0.7, -1.1, 2.0, 0.45, 0.50, (70, 74, 110)),
    (0.9, -1.1, 2.6, 0.62, 0.55, (62, 68, 104)),
    (-1.9, -1.2, 3.0, 0.70, 0.78, (34, 40, 64)),
    (0.05, -1.25, 3.2, 0.68, 0.92, (20, 24, 44)),
    (1.95, -1.2, 2.9, 0.72, 0.80, (30, 36, 60)),
]


def _mist(Y):
    t = np.clip((Y + 1.3) / 2.6, 0.0, 1.0)
    top = np.array([196, 198, 224], dtype=np.float64)
    bot = np.array([150, 150, 190], dtype=np.float64)
    return top[:, None, None] * t + bot[:, None, None] * (1 - t)


def _scene(X, Y):
    base = _mist(Y)
    r, g, b = base[0].copy(), base[1].copy(), base[2].copy()
    for cx, by, h, hw, op, tint in _TREES:
        m = S.fir(X, Y, cx, by, h, hw, seed=cx) * op
        r = r * (1 - m) + tint[0] * m
        g = g * (1 - m) + tint[1] * m
        b = b * (1 - m) + tint[2] * m
    # the bird, gliding in open sky (upper-left, clear of the tree line)
    bm = S.bird(X, Y, cx=-0.55, cy=0.92, size=0.34, droop=0.5)
    r = r * (1 - bm) + 22 * bm
    g = g * (1 - bm) + 24 * bm
    b = b * (1 - bm) + 40 * bm
    return r, g, b


def render(width=1000, height=700):
    canvas = Canvas.yeganeh(width, height, scale=height / 2.6)
    cache = {}

    def chan(i):
        def fn(X, Y):
            if "rgb" not in cache:
                cache["rgb"] = _scene(X, Y)
            return cache["rgb"][i]
        return fn

    return render_rgb(canvas, chan(0), chan(1), chan(2), intensity=clip255)
