"""Vectorise a mask into a Cricut-ready SVG (silhouette or negative stencil).

Everything funnels through a boolean **mask**:
  - a registered work, rendered then thresholded (dark pixels = mask), or
  - a parametric design drawn as thick strokes (see `mathart.sacred`).

Two outputs, both as a single `<path fill-rule="evenodd">` (Design Space imports
it as one cut layer, neutral units — you set the real size on import):

  - **silhouette**: the mask's own contours (counters/holes handled by evenodd).
  - **negative**: a full frame minus the motif, with auto **bridges** so interior
    islands (e.g. the inside of an "O", a sun disk) stay attached to the frame.

The vectoriser is marching squares (sub-pixel contours) + Douglas–Peucker
simplification — pure numpy, no extra dependencies.
"""

from __future__ import annotations

from collections import defaultdict, deque
from typing import List, Sequence, Tuple

import numpy as np

Point = Tuple[float, float]
Contour = List[Point]

# corner bits: TL*8 | TR*4 | BR*2 | BL*1  ->  segments between edges T,R,B,L
_CASES = {
    0: [], 15: [],
    1: [("L", "B")], 2: [("B", "R")], 3: [("L", "R")],
    4: [("T", "R")], 6: [("T", "B")], 7: [("L", "T")],
    8: [("T", "L")], 9: [("T", "B")], 11: [("T", "R")],
    12: [("L", "R")], 13: [("B", "R")], 14: [("L", "B")],
    5: [("L", "T"), ("B", "R")],   # saddle
    10: [("T", "R"), ("B", "L")],  # saddle
}


def _interp(a: float, b: float, t: float) -> float:
    if a == b:
        return 0.5
    return (t - a) / (b - a)


def marching_squares(field: np.ndarray, level: float = 0.5) -> List[Contour]:
    """Iso-contours of `field` at `level`, stitched into closed loops."""
    f = np.asarray(field, dtype=np.float64)
    h, w = f.shape
    segs: List[Tuple[Point, Point]] = []

    for i in range(h - 1):
        for j in range(w - 1):
            tl, tr = f[i, j], f[i, j + 1]
            bl, br = f[i + 1, j], f[i + 1, j + 1]
            idx = ((tl > level) << 3) | ((tr > level) << 2) \
                | ((br > level) << 1) | (bl > level)
            cases = _CASES[idx]
            if not cases:
                continue
            pt = {
                "T": (j + _interp(tl, tr, level), float(i)),
                "R": (j + 1.0, i + _interp(tr, br, level)),
                "B": (j + _interp(bl, br, level), i + 1.0),
                "L": (float(j), i + _interp(tl, bl, level)),
            }
            for e0, e1 in cases:
                segs.append((pt[e0], pt[e1]))

    return _stitch(segs)


def _stitch(segs: Sequence[Tuple[Point, Point]]) -> List[Contour]:
    def key(p: Point) -> Tuple[int, int]:
        return (round(p[0] * 1000), round(p[1] * 1000))

    adj: dict = defaultdict(list)  # key -> list of (neighbor_key, coord)
    coord: dict = {}
    for a, b in segs:
        ka, kb = key(a), key(b)
        coord[ka], coord[kb] = a, b
        adj[ka].append(kb)
        adj[kb].append(ka)

    contours: List[Contour] = []
    while adj:
        start = next(iter(adj))
        if not adj[start]:
            del adj[start]
            continue
        loop = [start]
        cur = start
        prev = None
        while True:
            nbrs = adj[cur]
            nxt = None
            for k in nbrs:
                if k != prev or len(nbrs) == 1:
                    nxt = k
                    break
            if nxt is None:
                nxt = nbrs[0]
            # consume edge in both directions
            adj[cur].remove(nxt)
            adj[nxt].remove(cur)
            if not adj[cur]:
                del adj[cur]
            prev, cur = cur, nxt
            if cur == start:
                break
            loop.append(cur)
            if not adj.get(cur):
                break
        if len(loop) >= 3:
            contours.append([coord[k] for k in loop])
    return contours


def _rdp_open(seq: Contour, eps: float) -> Contour:
    """Douglas–Peucker on an OPEN polyline (distinct endpoints)."""
    if len(seq) < 3:
        return seq
    x0, y0 = seq[0]
    x1, y1 = seq[-1]
    dx, dy = x1 - x0, y1 - y0
    norm = (dx * dx + dy * dy) ** 0.5 or 1e-9
    dmax, idx = 0.0, 0
    for i in range(1, len(seq) - 1):
        px, py = seq[i]
        d = abs(dy * px - dx * py + x1 * y0 - y1 * x0) / norm
        if d > dmax:
            dmax, idx = d, i
    if dmax > eps:
        left = _rdp_open(seq[:idx + 1], eps)
        right = _rdp_open(seq[idx:], eps)
        return left[:-1] + right
    return [seq[0], seq[-1]]


def _rdp(pts: Contour, eps: float) -> Contour:
    """Simplify a CLOSED contour by splitting it at its two extreme points."""
    if len(pts) < 4 or eps <= 0:
        return pts
    # split point = vertex farthest from pts[0] -> two open chains
    p0 = pts[0]
    k = max(range(len(pts)),
            key=lambda i: (pts[i][0] - p0[0]) ** 2 + (pts[i][1] - p0[1]) ** 2)
    if k == 0:
        return pts
    chain1 = _rdp_open(pts[:k + 1], eps)
    chain2 = _rdp_open(pts[k:] + [pts[0]], eps)
    out = chain1[:-1] + chain2[:-1]   # drop shared join + closing duplicate
    return out


def contours_to_d(contours: List[Contour], eps: float = 0.6,
                  precision: int = 2) -> str:
    """Combine contours into one SVG path data string (subpaths + Z)."""
    parts = []
    for c in contours:
        c = _rdp(c, eps)
        if len(c) < 3:
            continue
        fmt = f"%.{precision}f"
        d = "M" + " L".join(f"{fmt % x},{fmt % y}" for x, y in c) + "Z"
        parts.append(d)
    return " ".join(parts)


def _svg(d: str, width: int, height: int) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}">\n'
        f'  <path d="{d}" fill="#000000" fill-rule="evenodd" stroke="none"/>\n'
        f'</svg>\n'
    )


def _downscale(mask: np.ndarray, max_side: int) -> np.ndarray:
    h, w = mask.shape
    s = max(1, int(np.ceil(max(h, w) / max_side)))
    if s == 1:
        return mask
    return mask[::s, ::s]


# ---------------------------------------------------------------- bridges ----

def _label(mask: np.ndarray) -> Tuple[np.ndarray, int]:
    """8-connected labeling of True pixels. Returns (labels, count)."""
    h, w = mask.shape
    labels = np.zeros((h, w), dtype=np.int32)
    cur = 0
    nbr = [(-1, -1), (-1, 0), (-1, 1), (0, -1),
           (0, 1), (1, -1), (1, 0), (1, 1)]
    for i in range(h):
        for j in range(w):
            if mask[i, j] and labels[i, j] == 0:
                cur += 1
                q = deque([(i, j)])
                labels[i, j] = cur
                while q:
                    y, x = q.popleft()
                    for dy, dx in nbr:
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < h and 0 <= nx < w \
                                and mask[ny, nx] and labels[ny, nx] == 0:
                            labels[ny, nx] = cur
                            q.append((ny, nx))
    return labels, cur


def _stamp_segment(mask: np.ndarray, p0, p1, width: float) -> None:
    """Paint a thick segment (True) into mask."""
    r = max(1, int(round(width / 2)))
    (y0, x0), (y1, x1) = p0, p1
    n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    ys = np.linspace(y0, y1, n).round().astype(int)
    xs = np.linspace(x0, x1, n).round().astype(int)
    h, w = mask.shape
    for cy, cx in zip(ys, xs):
        y_lo, y_hi = max(0, cy - r), min(h, cy + r + 1)
        x_lo, x_hi = max(0, cx - r), min(w, cx + r + 1)
        mask[y_lo:y_hi, x_lo:x_hi] = True


def _add_bridges(material: np.ndarray, bridge_width: float) -> np.ndarray:
    """Tie every floating island of `material` to the main (largest) body.

    The material is inset from the image edge by the frame, so "main" can't be
    found by touching the border; we take the largest connected component as the
    stencil body and bridge each remaining island to it by its nearest point.
    """
    labels, n = _label(material)
    if n <= 1:
        return material
    sizes = np.bincount(labels.ravel())
    sizes[0] = 0                      # ignore background label 0
    main_lab = int(sizes.argmax())
    main_pts = np.argwhere(labels == main_lab)
    out = material.copy()
    for lab in range(1, n + 1):
        if lab == main_lab:
            continue
        isl = np.argwhere(labels == lab)
        if len(isl) == 0:
            continue
        # subsample both point sets for a fast nearest-pair search
        a = isl[np.linspace(0, len(isl) - 1, min(len(isl), 300)).astype(int)]
        b = main_pts[np.linspace(0, len(main_pts) - 1,
                                 min(len(main_pts), 600)).astype(int)]
        d2 = ((a[:, None, :] - b[None, :, :]) ** 2).sum(-1)
        ia, ib = np.unravel_index(d2.argmin(), d2.shape)
        _stamp_segment(out, tuple(a[ia]), tuple(b[ib]), bridge_width)
    return out


# ----------------------------------------------------------------- public ----

def silhouette_svg(mask: np.ndarray, max_side: int = 360,
                   eps: float = 0.6) -> str:
    m = _downscale(np.asarray(mask, dtype=bool), max_side)
    h, w = m.shape
    contours = marching_squares(m.astype(float), 0.5)
    return _svg(contours_to_d(contours, eps), w, h)


def negative_svg(mask: np.ndarray, frame_margin: int = 12,
                 bridge_width: float = 6.0, max_side: int = 360,
                 eps: float = 0.6, gap: int = 10) -> str:
    m = _downscale(np.asarray(mask, dtype=bool), max_side)
    margin = max(2, int(frame_margin))
    # pad so the motif never touches the frame -> a clean material ring + an
    # intact outer frame contour with the motif as an interior hole.
    pad = margin + max(2, int(gap))
    m = np.pad(m, pad, mode="constant", constant_values=False)
    h, w = m.shape
    frame = np.zeros((h, w), dtype=bool)
    frame[margin:h - margin, margin:w - margin] = True
    material = frame & ~m              # paint passes where the motif is
    material = _add_bridges(material, bridge_width)
    contours = marching_squares(material.astype(float), 0.5)
    return _svg(contours_to_d(contours, eps), w, h)


def mask_from_image(img, threshold: int = 128, invert: bool = False) -> np.ndarray:
    """Dark pixels -> True (motif). `invert` flips it."""
    arr = np.asarray(img.convert("L"), dtype=np.uint8)
    mask = arr < threshold
    return ~mask if invert else mask


# ------------------------------------------------- complex-image reductions ---
# Turn a photographic / AI-generated raster into cuttable masks. A flat
# `threshold` only works on already-binary art; these two handle tone and line.

def posterize_masks(img, levels: int = 3, invert: bool = False):
    """Quantise luminance into `levels` tone bands -> one mask per dark band.

    Returns a list of boolean masks ordered darkest-first (each a cut layer for
    a multi-tone stencil). The lightest band (≈ paper/background) is dropped.
    """
    levels = max(2, int(levels))
    arr = np.asarray(img.convert("L"), dtype=np.float64) / 255.0
    if invert:
        arr = 1.0 - arr
    q = np.clip((arr * levels).astype(int), 0, levels - 1)  # 0..levels-1
    masks = []
    for band in range(levels - 1):              # drop the lightest band
        masks.append(q <= band)                 # cumulative: darker ⊆ lighter
    return masks


def _sobel(gray: np.ndarray) -> np.ndarray:
    kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float64)
    ky = kx.T

    def conv(k):
        p = np.pad(gray, 1, mode="edge")
        out = np.zeros_like(gray)
        for di in range(3):
            for dj in range(3):
                out += k[di, dj] * p[di:di + gray.shape[0],
                                     dj:dj + gray.shape[1]]
        return out

    return np.hypot(conv(kx), conv(ky))


def edge_mask(img, threshold: float = 0.18, thickness: int = 1) -> np.ndarray:
    """Sobel edge magnitude -> boolean line-art mask (good for tracing stencils).

    `threshold` is on the normalised gradient (0..1); `thickness` dilates the
    edges so thin lines survive as a paintable band.
    """
    gray = np.asarray(img.convert("L"), dtype=np.float64) / 255.0
    mag = _sobel(gray)
    mag /= (mag.max() + 1e-9)
    edges = mag > threshold
    for _ in range(max(0, int(thickness) - 1)):
        e = edges.copy()
        e[1:, :] |= edges[:-1, :]
        e[:-1, :] |= edges[1:, :]
        e[:, 1:] |= edges[:, :-1]
        e[:, :-1] |= edges[:, 1:]
        edges = e
    return edges
