"""Parametric sacred-geometry masks (base-12 wheel, rose seal).

These draw thick strokes into a boolean mask so they flow through the same
stencil pipeline as any other work (`mathart.stencil`). Drive them from the
numerology of a word: `C.S` sets the inner rhythm, the wheel always has 12 gates.
"""

from __future__ import annotations

import numpy as np

from .stencil import _stamp_segment  # thick-segment rasteriser

# glyph types per gate: 0=segment, 1=angle L, 2=chevron, 3=hook
_GLYPH_TYPES = [0, 1, 2, 1, 3, 0, 1, 2, 1, 3, 0, 2]
_GLYPH_TWIST = [0, 20, -15, 35, -30, 10, 25, -20, 15, -10, 30, -25]


def _blank(size: int) -> np.ndarray:
    return np.zeros((size, size), dtype=bool)


def _seg(mask, x0, y0, x1, y1, width):
    # stencil._stamp_segment works in (row, col) = (y, x)
    _stamp_segment(mask, (y0, x0), (y1, x1), width)


def _polyline(mask, pts, width):
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        _seg(mask, x0, y0, x1, y1, width)


def _glyph(mask, cx, cy, ang, gtype, twist_deg, L, width):
    a = ang + np.radians(twist_deg)
    ca, sa = np.cos(a), np.sin(a)

    def place(px, py):
        # local (px,py) rotated by a, translated to (cx,cy)
        return (cx + px * ca - py * sa, cy + px * sa + py * ca)

    if gtype == 0:        # segment
        pts = [(10, 0), (10 + L, 0)]
    elif gtype == 1:      # angle L
        pts = [(10, 0), (10 + L * 0.75, 0), (10 + L * 0.75, -L * 0.45)]
    elif gtype == 2:      # chevron
        pts = [(10, 0), (10 + L * 0.55, -L * 0.35), (10 + L, 0)]
    else:                 # hook
        pts = [(10, 0), (10 + L * 0.65, 0), (10 + L * 0.65, L * 0.35)]
    _polyline(mask, [place(px, py) for px, py in pts], width)


def rose_seal_mask(size: int = 600, turns: int = 3, line_width: int = 5,
                   amp_struct: float = 0.18, amp_cycle: float = 0.10) -> np.ndarray:
    """Central rose/seal curve r(a)=base(1+A4 sin4a+A12 sin12a+0.08a)."""
    mask = _blank(size)
    cx = cy = size / 2
    base = 0.11 * size
    pts = []
    a = 0.0
    a_max = 2 * np.pi * turns
    while a <= a_max:
        r = base * (1 + amp_struct * np.sin(4 * a)
                    + amp_cycle * np.sin(12 * a) + 0.08 * a)
        pts.append((cx + r * np.cos(a), cy + r * np.sin(a)))
        a += 0.02
    _polyline(mask, pts, line_width)
    return mask


def wheel_base12_mask(size: int = 700, cs: int = 3, line_width: int = 6,
                      with_seal: bool = True,
                      with_quadrature: bool = True) -> np.ndarray:
    """12-gate wheel of glyphs + ring + (optional) central seal & quadrature.

    `cs` (Code Secret) groups the gates: cs=3 -> 4 gates per breath, etc.
    Returned as a thick-stroke mask ready for `mathart.stencil`.
    """
    mask = _blank(size)
    cx = cy = size / 2
    R = 0.33 * size
    L = 0.05 * size

    # outer guide ring
    ring = [(cx + R * np.cos(t), cy + R * np.sin(t))
            for t in np.linspace(0, 2 * np.pi, 240)]
    _polyline(mask, ring, max(2, line_width - 2))

    # 12 glyphs + dot at each gate
    for i in range(12):
        ang = -np.pi / 2 + i * 2 * np.pi / 12
        gx, gy = cx + R * np.cos(ang), cy + R * np.sin(ang)
        # dot
        r = max(2, line_width)
        y0, y1 = int(gy - r), int(gy + r + 1)
        x0, x1 = int(gx - r), int(gx + r + 1)
        mask[max(0, y0):y1, max(0, x0):x1] = True
        _glyph(mask, gx, gy, ang, _GLYPH_TYPES[i], _GLYPH_TWIST[i], L, line_width)

    # quadrature: 4 lines from centre (the 4 planes)
    if with_quadrature:
        for k in range(4):
            a = -np.pi / 2 + k * np.pi / 2
            _seg(mask, cx, cy, cx + (R - 40) * np.cos(a),
                 cy + (R - 40) * np.sin(a), max(2, line_width - 3))

    if with_seal:
        seal = rose_seal_mask(size, line_width=line_width)
        mask |= seal

    # mark the cs grouping faintly is omitted in a stencil (binary); cs only
    # affects which gates one would colour — geometry stays the full 12.
    _ = cs
    return mask


def _circle(mask, cx, cy, r, width, segments: int = 200):
    ts = np.linspace(0, 2 * np.pi, segments)
    pts = [(cx + r * np.cos(t), cy + r * np.sin(t)) for t in ts]
    _polyline(mask, pts, width)


def flower_of_life_mask(size: int = 700, line_width: int = 4,
                        with_border: bool = True) -> np.ndarray:
    """Classic Flower of Life: 19 overlapping circles on a triangular lattice."""
    mask = _blank(size)
    cx = cy = size / 2
    R = 0.15 * size
    centers = []
    for q in range(-2, 3):
        for r in range(-2, 3):
            x = R * (q + r * 0.5)
            y = R * (r * np.sqrt(3) / 2)
            if x * x + y * y <= (2 * R) ** 2 + 1e-6:
                centers.append((cx + x, cy + y))
    for x, y in centers:
        _circle(mask, x, y, R, line_width)
    if with_border:
        _circle(mask, cx, cy, 3 * R, line_width)
        _circle(mask, cx, cy, 3 * R + line_width * 1.6, line_width)
    return mask


def metatron_cube_mask(size: int = 700, line_width: int = 3) -> np.ndarray:
    """Fruit of Life (13 circles) with every centre joined — Metatron's Cube."""
    mask = _blank(size)
    cx = cy = size / 2
    d = 0.18 * size
    centers = [(cx, cy)]
    for k in range(6):
        a = k * np.pi / 3
        centers.append((cx + d * np.cos(a), cy + d * np.sin(a)))
        centers.append((cx + 2 * d * np.cos(a), cy + 2 * d * np.sin(a)))
    # connect every pair of centres (the "cube")
    for i in range(len(centers)):
        for j in range(i + 1, len(centers)):
            _seg(mask, *centers[i], *centers[j], max(1, line_width - 1))
    # the 13 circles on top
    for x, y in centers:
        _circle(mask, x, y, d * 0.5, line_width)
    return mask


def mandala_mask(size: int = 700, petals: int = 12, line_width: int = 4,
                 rings: int = 3) -> np.ndarray:
    """Radial mandala: concentric rings + rose petals + spokes (N-fold)."""
    mask = _blank(size)
    cx = cy = size / 2
    Rmax = 0.42 * size
    # concentric guide rings
    for i in range(1, rings + 1):
        _circle(mask, cx, cy, Rmax * i / (rings + 1), max(2, line_width - 1))
    # rose curves r = R(1 + 0.3 cos(petals*theta)) at two scales
    for scale in (0.62, 0.95):
        pts = []
        for t in np.linspace(0, 2 * np.pi, 720):
            r = Rmax * scale * (0.7 + 0.3 * np.cos(petals * t))
            pts.append((cx + r * np.cos(t), cy + r * np.sin(t)))
        _polyline(mask, pts, line_width)
    # spokes
    for k in range(petals):
        a = k * 2 * np.pi / petals
        _seg(mask, cx, cy, cx + Rmax * np.cos(a), cy + Rmax * np.sin(a),
             max(1, line_width - 2))
    _circle(mask, cx, cy, Rmax, line_width)
    return mask


GENERATORS = {
    "wheel": wheel_base12_mask,
    "seal": rose_seal_mask,
    "flower": flower_of_life_mask,
    "metatron": metatron_cube_mask,
    "mandala": mandala_mask,
}
