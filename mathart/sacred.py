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


def _triangle(mask, cx, cy, r, rot, width):
    """Equilateral triangle inscribed in radius `r`, rotated by `rot` rad."""
    pts = [(cx + r * np.cos(rot + k * 2 * np.pi / 3),
            cy + r * np.sin(rot + k * 2 * np.pi / 3)) for k in range(3)]
    _polyline(mask, pts + [pts[0]], width)


def golden_spiral_mask(size: int = 700, line_width: int = 4,
                       turns: float = 3.5, with_rects: bool = True) -> np.ndarray:
    """Logarithmic (golden) spiral r=a·φ^(2θ/π) + nested golden rectangles."""
    mask = _blank(size)
    cx = cy = size / 2
    phi = (1 + np.sqrt(5)) / 2
    b = np.log(phi) / (np.pi / 2)          # growth per quarter turn = φ
    a_max = 2 * np.pi * turns
    base = 0.42 * size / np.exp(b * a_max)  # outer end lands at 0.42·size
    pts = []
    a = 0.0
    while a <= a_max:
        r = base * np.exp(b * a)
        pts.append((cx + r * np.cos(a), cy + r * np.sin(a)))
        a += 0.03
    _polyline(mask, pts, line_width)
    if with_rects:
        # nested golden rectangles whose corners ride the spiral (quarter steps)
        rpts = []
        a = 0.0
        while a <= a_max:
            r = base * np.exp(b * a)
            rpts.append((cx + r * np.cos(a), cy + r * np.sin(a)))
            a += np.pi / 2
        _polyline(mask, rpts, max(1, line_width - 1))
    return mask


def enneagram_mask(size: int = 700, line_width: int = 4) -> np.ndarray:
    """Classic enneagram: outer circle, 3-6-9 triangle, 1-4-2-8-5-7 web."""
    mask = _blank(size)
    cx = cy = size / 2
    R = 0.4 * size
    _circle(mask, cx, cy, R, max(2, line_width - 1))

    def P(i):  # point i in 1..9, point 9 at top, clockwise
        ang = -np.pi / 2 + (i % 9) * 2 * np.pi / 9
        return (cx + R * np.cos(ang), cy + R * np.sin(ang))

    triangle = [P(9), P(3), P(6), P(9)]
    _polyline(mask, triangle, line_width)
    web = [P(1), P(4), P(2), P(8), P(5), P(7), P(1)]
    _polyline(mask, web, line_width)
    return mask


def sri_yantra_mask(size: int = 760, line_width: int = 3) -> np.ndarray:
    """Stylised Sri Yantra: 9 interlocking triangles, lotus petals, bhupura."""
    mask = _blank(size)
    cx = cy = size / 2
    R = 0.26 * size
    # 4 upward (Shiva) + 5 downward (Shakti) triangles at descending scales
    up = [1.00, 0.74, 0.50, 0.28]
    dn = [1.06, 0.84, 0.62, 0.40, 0.20]
    for s in up:
        _triangle(mask, cx, cy, R * s, -np.pi / 2, line_width)
    for s in dn:
        _triangle(mask, cx, cy, R * s, np.pi / 2, line_width)
    # central bindu dot
    rr = max(2, line_width)
    mask[int(cy - rr):int(cy + rr + 1), int(cx - rr):int(cx + rr + 1)] = True
    # two lotus rings (8 + 16 petals) as small arcs/circles
    for n, rad in ((8, 1.18), (16, 1.40)):
        rr2 = R * rad
        for k in range(n):
            a = k * 2 * np.pi / n
            px, py = cx + rr2 * np.cos(a), cy + rr2 * np.sin(a)
            _circle(mask, px, py, 0.045 * size, max(2, line_width - 1), 40)
    # bhupura: outer square frame with T-gates
    s2 = R * 1.62
    sq = [(cx - s2, cy - s2), (cx + s2, cy - s2),
          (cx + s2, cy + s2), (cx - s2, cy + s2), (cx - s2, cy - s2)]
    _polyline(mask, sq, line_width)
    for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
        mx, my = cx + dx * s2, cy + dy * s2
        gate = 0.08 * size
        if dx == 0:
            _polyline(mask, [(mx - gate, my), (mx - gate, my + dy * gate),
                             (mx + gate, my + dy * gate), (mx + gate, my)],
                      line_width)
        else:
            _polyline(mask, [(mx, my - gate), (mx + dx * gate, my - gate),
                             (mx + dx * gate, my + gate), (mx, my + gate)],
                      line_width)
    return mask


GENERATORS = {
    "wheel": wheel_base12_mask,
    "seal": rose_seal_mask,
    "flower": flower_of_life_mask,
    "metatron": metatron_cube_mask,
    "mandala": mandala_mask,
    "spiral": golden_spiral_mask,
    "enneagram": enneagram_mask,
    "sri-yantra": sri_yantra_mask,
}
