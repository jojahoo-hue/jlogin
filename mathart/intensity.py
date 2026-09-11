"""Intensity function F, transcribed exactly from Yeganeh's works.

    F(x) = floor( | 255 * e^(-e^(-1000 x)) * |x| * e^(-e^(1000 (x-1))) | )

Both factors are DOUBLE exponentials forming a soft window:
  e^(-e^(-1000 x))   ~ smooth step 0 (x<0) -> 1 (x>0)
  e^(-e^(1000(x-1)))  ~ smooth step 1 (x<1) -> 0 (x>1)
so F(x) behaves like floor(255 * clamp(x, 0, 1)). Channel functions R/G/B are
designed to land in ~[0, 1]; F maps them to a 0..255 byte.
"""

from __future__ import annotations

import numpy as np


def F(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    lo = np.clip(-1000.0 * x, -700.0, 700.0)        # e^(-e^(-1000x))
    hi = np.clip(1000.0 * (x - 1.0), -700.0, 700.0)  # e^(-e^(1000(x-1)))
    val = 255.0 * np.exp(-np.exp(lo)) * np.abs(x) * np.exp(-np.exp(hi))
    return np.clip(np.floor(np.abs(val)), 0.0, 255.0)
