"""primitives.py - the reusable vocabulary of Yeganeh-style math art.

His formulas look monstrous, but they are assembled from a handful of recurring
patterns. Naming them here is what lets you (or Claude Code) *compose* new works
instead of re-deriving pages of symbols. Everything is vectorized over numpy
arrays (the (X, Y) grids from canvas.Canvas).

Patterns observed across the forest / turbines / horse formulas:

  - double exponential       e^(-e^(u))          smooth one-sided cutoff
  - soft step / window       e^(-e^(k(x-c)))     turn on/off around c
  - gaussian bump            e^(-(d/w)^2)         a localized blob
  - arctan envelope          1/2 + (1/pi) arctan  smooth 0->1 ramp
  - finite product  PROD     layer / mask many instances (the horse's prod)
  - finite sum      SUM      add many strokes/objects (turbines' k=1..40)
  - trig combinator          cos/sin mixes that bend straight lines into shapes
"""

from __future__ import annotations

from typing import Callable
import numpy as np

Field = np.ndarray  # an array over the (X, Y) grid


# --------------------------------------------------------------------------
# exponential envelopes
# --------------------------------------------------------------------------
def double_exp(u: Field) -> Field:
    """e^(-e^(u)). The signature Yeganeh move: a smooth, very sharp cutoff.

    ~1 when u is very negative, drops to 0 as u grows past ~0.
    """
    return np.exp(-np.exp(np.clip(u, -700, 700)))


def soft_step(x: Field, center: float = 0.0, k: float = 50.0) -> Field:
    """Smooth 1 -> 0 transition as x rises through `center`. Larger k = sharper."""
    return double_exp(k * (x - center))


def soft_window(x: Field, lo: float, hi: float, k: float = 50.0) -> Field:
    """~1 inside [lo, hi], ~0 outside, with soft edges."""
    return soft_step(-x, -lo, k) * soft_step(x, hi, k)


def bump(distance: Field, width: float = 1.0) -> Field:
    """Gaussian-like blob: 1 at distance 0, fading over `width`."""
    return np.exp(-(distance / width) ** 2)


def arctan_env(u: Field) -> Field:
    """1/2 + (1/pi) arctan(u): a smooth 0 -> 1 ramp."""
    return 0.5 + np.arctan(u) / np.pi


# --------------------------------------------------------------------------
# layering: the big PROD / SUM operators
# --------------------------------------------------------------------------
def stack_sum(term: Callable[[int], Field], start: int, end: int) -> Field:
    """SUM_{s=start}^{end} term(s). Use to ADD many objects (e.g. N turbines)."""
    acc = None
    for s in range(start, end + 1):
        t = term(s)
        acc = t if acc is None else acc + t
    return acc


def stack_product(factor: Callable[[int], Field], start: int, end: int) -> Field:
    """PROD_{s=start}^{end} factor(s). Use to MASK / intersect many regions."""
    acc = None
    for s in range(start, end + 1):
        f = factor(s)
        acc = f if acc is None else acc * f
    return acc


# --------------------------------------------------------------------------
# shape helpers (turning coordinates into curved strokes)
# --------------------------------------------------------------------------
def warp(x: Field, *, amp: float, freq: float, phase: float = 0.0) -> Field:
    """Add a sinusoidal wobble to a coordinate -> bends straight lines."""
    return x + amp * np.sin(freq * x + phase)


def clamp01(v: Field) -> Field:
    return np.clip(v, 0.0, 1.0)
