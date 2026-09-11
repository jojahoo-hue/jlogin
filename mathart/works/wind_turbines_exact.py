"""Transcription of "Wind Turbines" by Hamid Naderi Yeganeh.

1800 x 1000 image. Pixel (row n, column m):
    rgb( F(R(x,y)), F(G(x,y)), F(B(x,y)) ),   x=(m-980)/900, y=(951-n)/900.

LEGIBILITY NOTE. Transcribed VERBATIM from the photo (high confidence):
  - F (the double-exponential byte clamp), the (x,y) pixel mapping,
  - the sun term  s = 16x^2 + 16(y-1/5)^2 - 3/5,
  - the gradient phase  g(a,b) = y + a cos(3x) + b sin(5x),
  - the R channel (broad red sky + thin bright horizon band).
BELOW the photo's resolution (best-effort, NOT byte-exact):
  - the fine structure of G and B (which exponentials are single vs double),
  - the turbine sum A(x,y) with its deeply nested |.| exponents, C_k, D_k.
Give the formula as text or a higher-res image and these slot straight in.
"""

from __future__ import annotations

import numpy as np

from ..canvas import Canvas
from ..renderers import render_rgb
from ..intensity import F


def _s(x, y):
    return 16.0 * x**2 + 16.0 * (y - 1 / 5) ** 2 - 3 / 5       # sun circle


def _g(x, y, a, b):
    return y + a * np.cos(3.0 * x) + b * np.sin(5.0 * x)      # gradient phase


def _de(u):
    return np.exp(-np.exp(np.clip(u, -700, 700)))            # e^(-e^(u))


# --- channels (R verbatim; G,B best-effort) --------------------------------
def R(x, y, A=0.0):
    return 0.3 * np.exp(np.clip(-1000.0 * _g(x, y, 1/200, 1/100), -700, 700)) \
        - A + _de(-200.0 * _g(x, y, 1/100, 1/200))


def G(x, y, A=0.0):
    ring = 1.0 - 0.6 * np.exp(-100.0 * _s(x, y) ** 2)
    return 0.1 - A + ring * (x**2 + (y - 1/5) ** 2) \
        * np.exp(np.clip(-200.0 * _g(x, y, 1/200, 1/100), -700, 700))


def B(x, y, A=0.0):
    return _de(20.0 * _s(x, y)) \
        * np.exp(np.clip(-200.0 * _g(x, y, 1/100, 1/200), -700, 700)) - A


# --- best-effort turbine sum (structure only) ------------------------------
def turbine_mask(x, y):
    A = np.zeros_like(x)
    for k in range(1, 41):
        sc = (9 / 10) ** k
        off = np.cos(float(k) ** 7)
        tilt = 3/5 + 3/10 * np.cos(float(k) ** 4)
        hub = (7/10) * sc
        tower = _de(500 * (np.abs(x + off) - 0.008 * sc)) \
            * _de(-400 * y) * _de(700 * (y - hub))
        Dk = (x + off) ** 2 + tilt**2 * (y - hub) ** 2
        rotor = np.exp(-50.0 * np.abs(Dk - 0.018 * sc * sc))
        A = np.maximum(A, 1.4 * np.clip(tower + rotor, 0, 1))
    return np.clip(A, 0.0, 1.4)


def render(width=1800, height=1000, turbines=False):
    canvas = Canvas(width=width, height=height,
                    x0=width * 980 / 1800, x_scale=width / 2.0,
                    y0=height * 951 / 1000, y_scale=height * 0.9)
    store = {}

    def chan(fn):
        def f(X, Y):
            if turbines and "A" not in store:
                store["A"] = turbine_mask(X, Y)
            return fn(X, Y, store.get("A", 0.0))
        return f

    return render_rgb(canvas, chan(R), chan(G), chan(B), intensity=F)
