"""Galloping Silhouette - Family 2 (set work), in the spirit of the horse.

Image is { (x, y) | T(x, y) > 0 }, built as a union of body parts from the
shapes library (shapes.ellipse, shapes.capsule) plus a tail streamed with
stack_sum. Swap T for the transcribed A_v / P_s / Q_s / W expressions for the
exact published "Running Horse".
"""

from __future__ import annotations

import numpy as np

from ..canvas import Canvas
from ..renderers import render_set
from .. import shapes as S
from .. import primitives as P


def T(X, Y):
    parts = [
        S.ellipse(X, Y, 0.0, 0.05, 0.95, 0.40),          # barrel / body
        S.capsule(X, Y, 0.55, 0.20, 1.00, 0.78, 0.20),   # neck
        S.ellipse(X, Y, 1.10, 0.92, 0.18, 0.26, -0.35),  # head
        S.ellipse(X, Y, 1.28, 1.05, 0.05, 0.12, -0.3),   # muzzle / ear
        S.capsule(X, Y, 0.62, -0.20, 0.95, -1.05, 0.10), # front leg reaching
        S.capsule(X, Y, 0.45, -0.20, 0.30, -0.95, 0.10), # front leg tucked
        S.capsule(X, Y, -0.55, -0.20, -0.78, -1.05, 0.11),  # hind leg driving
        S.capsule(X, Y, -0.70, -0.18, -0.40, -0.80, 0.11),  # hind leg tucked
    ]
    field = S.union(*parts)

    def tail_stroke(s):
        drop = 0.10 * s
        sway = 0.18 * np.sin(1.6 * s)
        return S.capsule(X, Y, -0.85, 0.32 - 0.03 * s,
                         -1.65 - 0.04 * s, 0.05 - drop + sway, 0.075 - 0.004 * s)

    tail = P.stack_sum(tail_stroke, 0, 9)
    return np.maximum(field, tail)


def render(width=1100, height=900):
    canvas = Canvas.yeganeh(width, height, scale=height / 3.0)
    return render_set(canvas, T, ink=(15, 15, 20), background=(250, 250, 250))
