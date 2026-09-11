"""_template.py - copy this to start a new work.

Pick ONE family, delete the other, then register your render() in
works/__init__.py under REGISTRY.
"""

from __future__ import annotations

import numpy as np

from ..canvas import Canvas
from ..renderers import render_rgb, render_set, clip255
from ..intensity import F
from .. import primitives as P


# ---- Family 1: COLOR work -------------------------------------------------
def _color_scene(X, Y):
    # Build raw R, G, B fields here using primitives.
    r = 128 + 100 * np.sin(3 * X) * P.bump(Y, 1.0)
    g = 128 + 100 * np.cos(3 * Y)
    b = 128 + 100 * P.soft_window(X, -1, 1)
    return r, g, b


def render_color(width=1000, height=700):
    canvas = Canvas.yeganeh(width, height, scale=height / 2.5)
    cache = {}

    def chan(i):
        def fn(X, Y):
            if "s" not in cache:
                cache["s"] = _color_scene(X, Y)
            return cache["s"][i]
        return fn

    # intensity=F to match Yeganeh's encoding; clip255 for direct color.
    return render_rgb(canvas, chan(0), chan(1), chan(2), intensity=clip255)


# ---- Family 2: SET work ---------------------------------------------------
def _T(X, Y):
    # Ink where this is > 0. Union parts with np.maximum, intersect with *.
    disk = 1.0 - X**2 - Y**2
    ring = P.warp(X, amp=0.3, freq=8.0)  # example use of a primitive
    return np.maximum(disk, 0.1 - (np.abs(ring) - 0.8) ** 2)


def render_set_work(width=900, height=900):
    canvas = Canvas.yeganeh(width, height, scale=height / 2.5)
    return render_set(canvas, _T)


# default export expected by the registry:
render = render_color
