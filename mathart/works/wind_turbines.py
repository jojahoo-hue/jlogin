"""Wind Turbines at Sunset - Family 1 (color), in the spirit of Yeganeh's piece.

A radial sun glow over a hot gradient sky, with turbine silhouettes added by
stack_sum (one term per turbine -> the engine scales to a whole wind farm).
Original composition; swap R/G/B for the transcribed formulas + intensity=F for
the exact reproduction.
"""

from __future__ import annotations

import numpy as np

from ..canvas import Canvas
from ..renderers import render_rgb, clip255
from .. import primitives as P

# (center_x, base_y, scale, blade_phase)
_TURBINES = [
    (-1.7, -0.7, 0.55, 0.4), (-1.15, -0.75, 0.42, 1.7), (-0.55, -0.78, 0.30, 2.9),
    (0.0, -0.8, 0.22, 0.9), (0.6, -0.78, 0.30, 2.1), (1.2, -0.75, 0.45, 0.2),
    (1.75, -0.7, 0.58, 1.2),
]
_SUN = (0.15, -0.15, 0.42)  # cx, cy, radius


def _sky(X, Y):
    t = P.clamp01((Y + 0.85) / 1.7)                  # 0 ground .. 1 top
    r = 255 - 5 * (1 - t)
    g = 70 + 175 * t
    b = 10 + 20 * t
    # sun glow
    d = np.sqrt((X - _SUN[0]) ** 2 + (Y - _SUN[1]) ** 2)
    glow = P.bump(np.maximum(d - _SUN[2], 0.0), 0.25)
    disk = (d < _SUN[2]).astype(np.float64)
    light = np.clip(disk + 0.85 * glow, 0.0, 1.0)
    r = r * (1 - light) + 255 * light
    g = g * (1 - light) + 252 * light
    b = b * (1 - light) + 225 * light
    return r, g, b


def _turbine(X, Y, cx, by, sc, phase):
    mast = P.clamp01((0.018 * sc / 0.4 - np.abs(X - cx)) / 0.006) \
        * P.clamp01((Y - by) / 0.01) * P.clamp01((by + 1.7 * sc - Y) / 0.01)
    hub_y = by + 1.7 * sc
    mask = mast
    for k in range(3):
        ang = phase + k * 2 * np.pi / 3
        ex = cx + 0.9 * sc * np.cos(ang)
        ey = hub_y + 0.9 * sc * np.sin(ang)
        dx, dy = ex - cx, ey - hub_y
        L2 = dx * dx + dy * dy + 1e-9
        tt = np.clip(((X - cx) * dx + (Y - hub_y) * dy) / L2, 0.0, 1.0)
        px, py = cx + tt * dx, hub_y + tt * dy
        d2 = (X - px) ** 2 + (Y - py) ** 2
        blade = P.clamp01(((0.03 * sc) ** 2 - d2) / (0.01 * sc) ** 2)
        mask = np.maximum(mask, blade)
    return mask


def _scene(X, Y):
    r, g, b = _sky(X, Y)
    ground = P.clamp01((-0.8 - Y) / 0.02)
    r = r * (1 - ground) + 22 * ground
    g = g * (1 - ground) + 30 * ground
    b = b * (1 - ground) + 12 * ground
    silhouette = P.stack_sum(
        lambda i: _turbine(X, Y, *_TURBINES[i]), 0, len(_TURBINES) - 1
    )
    silhouette = P.clamp01(silhouette)
    r = r * (1 - silhouette) + 25 * silhouette
    g = g * (1 - silhouette) + 18 * silhouette
    b = b * (1 - silhouette) + 28 * silhouette
    return r, g, b


def render(width=1100, height=620):
    canvas = Canvas.yeganeh(width, height, scale=height / 1.85)
    cache = {}

    def chan(i):
        def fn(X, Y):
            if "s" not in cache:
                cache["s"] = _scene(X, Y)
            return cache["s"][i]
        return fn

    return render_rgb(canvas, chan(0), chan(1), chan(2), intensity=clip255)
