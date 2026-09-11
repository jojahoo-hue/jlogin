"""shapes.py - reusable procedural SHAPES, one level above primitives.py.

primitives.py = math atoms (envelopes, bumps, sums/products).
shapes.py     = recognizable forms built from those atoms: ellipses, capsules,
                fir trees, flying birds, sun glow, ridges, fractal-ish texture.

Convention:
  - "field" functions return a signed array (> 0 inside the shape) -> ideal for
    SET works and for unions via np.maximum / intersections via *.
  - "mask"  functions return a [0, 1] coverage array -> ideal for COLOR works,
    where you blend a color with `color*(1-m) + ink*m`.
  - `to_mask(field, edge)` converts a signed field into a soft [0, 1] mask.
"""

from __future__ import annotations

import numpy as np
from . import primitives as P

Field = np.ndarray


# --------------------------------------------------------------------------
# converters / combinators
# --------------------------------------------------------------------------
def to_mask(field: Field, edge: float = 0.01) -> Field:
    """Signed field (>0 inside) -> soft [0,1] coverage mask."""
    return P.clamp01(field / edge)


def union(*fields: Field) -> Field:
    out = fields[0]
    for f in fields[1:]:
        out = np.maximum(out, f)
    return out


def intersect(*fields: Field) -> Field:
    out = fields[0]
    for f in fields[1:]:
        out = np.minimum(out, f)
    return out


# --------------------------------------------------------------------------
# primitive geometry (signed fields, > 0 inside)
# --------------------------------------------------------------------------
def ellipse(X, Y, cx, cy, rx, ry, rot=0.0) -> Field:
    c, s = np.cos(rot), np.sin(rot)
    xr = (X - cx) * c + (Y - cy) * s
    yr = -(X - cx) * s + (Y - cy) * c
    return 1.0 - (xr / rx) ** 2 - (yr / ry) ** 2


def capsule(X, Y, x0, y0, x1, y1, w) -> Field:
    """Rounded segment (limb/stroke). > 0 within distance w of the segment."""
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy + 1e-9
    t = np.clip(((X - x0) * dx + (Y - y0) * dy) / L2, 0.0, 1.0)
    px, py = x0 + t * dx, y0 + t * dy
    d2 = (X - px) ** 2 + (Y - py) ** 2
    return w * w - d2


# --------------------------------------------------------------------------
# scene elements (return [0,1] masks, ready for color compositing)
# --------------------------------------------------------------------------
def fir(X, Y, cx, base, h, hw, edge=0.018, seed=0.0) -> Field:
    """Conifer silhouette mask with jagged branch wobble."""
    t = (Y - base) / h
    wobble = 1.0 + 0.18 * np.sin(38.0 * Y + seed) + 0.10 * np.sin(91.0 * Y + cx + seed)
    w = hw * np.clip(1.0 - t, 0.0, 1.0) * wobble
    return P.clamp01((w - np.abs(X - cx)) / edge) * P.clamp01((Y - base) / edge)


def bird(X, Y, cx, cy, size=0.2, droop=0.45, edge=0.01) -> Field:
    """Distant flying-bird silhouette (gull "m" shape) as a [0,1] mask."""
    body = capsule(X, Y, cx, cy, cx, cy - 0.15 * size, 0.10 * size)
    # each wing = two segments (shoulder up-out, tip drooping) -> a soft curve
    lw1 = capsule(X, Y, cx, cy, cx - 0.6 * size, cy + 0.35 * size, 0.10 * size)
    lw2 = capsule(X, Y, cx - 0.6 * size, cy + 0.35 * size,
                  cx - 1.0 * size, cy + (0.35 - droop) * size, 0.07 * size)
    rw1 = capsule(X, Y, cx, cy, cx + 0.6 * size, cy + 0.35 * size, 0.10 * size)
    rw2 = capsule(X, Y, cx + 0.6 * size, cy + 0.35 * size,
                  cx + 1.0 * size, cy + (0.35 - droop) * size, 0.07 * size)
    return to_mask(union(body, lw1, lw2, rw1, rw2), edge)


def sun_glow(X, Y, cx, cy, radius, halo=0.25) -> Field:
    """Light field in [0,1]: solid disk + soft halo. Blend toward a light color."""
    d = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    disk = (d < radius).astype(np.float64)
    glow = P.bump(np.maximum(d - radius, 0.0), halo)
    return np.clip(disk + 0.85 * glow, 0.0, 1.0)


def ridge(X, Y, base, amp=0.1, freq=2.0, edge=0.02) -> Field:
    """Rolling ground/hill mask: ink below a wavy horizon line."""
    line = base + amp * np.sin(freq * X) + 0.4 * amp * np.sin(2.7 * freq * X + 1.0)
    return P.clamp01((line - Y) / edge)


def fbm(X, Y, octaves=4, freq=1.5, seed=0.0) -> Field:
    """Cheap fractal-ish texture in ~[-1,1] from summed sines. For mist/foliage."""
    out = np.zeros_like(X)
    amp, f = 1.0, freq
    for o in range(octaves):
        out += amp * np.sin(f * X + 1.3 * o + seed) * np.cos(f * Y - 0.7 * o + seed)
        amp *= 0.5
        f *= 2.0
    return out
