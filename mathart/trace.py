"""Image → mathematical formula → image (Fourier epicycles), for pochoir series.

The missing half of the skill: take a *raster* image, recover a closed-form
parametric **formula** that reproduces its outline, regenerate the image from
that formula, and feed the same Cricut stencil pipeline. Because the formula is
a handful of complex Fourier coefficients, it is:

  - exact to the chosen number of harmonics (raise/lower = fidelity/abstraction),
  - storable/shareable as JSON (the coefficients *are* the formula),
  - editable → a whole **series on one theme**: stylise (drop harmonics),
    kaleidoscope (N-fold), morph (interpolate two images), modulate (organic
    jitter).

Pipeline:  image → mask (silhouette/edges/posterize) → contours (marching
squares, reused from `stencil`) → per-contour complex Fourier series → coeffs.
Regenerate:  z(t) = Σ_n c_n · e^{i·n·t}  sampled densely → thick-stroke mask.
"""

from __future__ import annotations

import json
from typing import List, Optional

import numpy as np

from . import stencil as st


# --------------------------------------------------------------- analysis ----

def _resample_closed(contour, n: int) -> Optional[np.ndarray]:
    """Resample a closed contour to `n` points evenly spaced by arc length."""
    pts = np.asarray(contour, dtype=np.float64)
    if len(pts) < 3:
        return None
    pts = np.vstack([pts, pts[0]])                  # close the loop
    seg = np.sqrt((np.diff(pts, axis=0) ** 2).sum(1))
    d = np.concatenate([[0.0], np.cumsum(seg)])
    total = d[-1]
    if total < 1e-9:
        return None
    target = np.linspace(0.0, total, n, endpoint=False)
    x = np.interp(target, d, pts[:, 0])
    y = np.interp(target, d, pts[:, 1])
    return x + 1j * y


def fourier_fit(contour, n_harmonics: int = 60, samples: int = 512):
    """Closed contour → (freqs, coeffs) keeping harmonics |n| ≤ n_harmonics."""
    z = _resample_closed(contour, samples)
    if z is None:
        return None
    N = len(z)
    C = np.fft.fft(z) / N
    freqs = np.fft.fftfreq(N, d=1.0 / N).round().astype(int)
    keep = np.abs(freqs) <= n_harmonics
    return freqs[keep], C[keep]


def fourier_eval(freqs, coeffs, samples: int = 2000) -> np.ndarray:
    """Evaluate z(t) = Σ c_n e^{i n t} at `samples` points over [0, 2π)."""
    t = np.linspace(0.0, 2 * np.pi, samples, endpoint=False)
    basis = np.exp(1j * np.outer(t, np.asarray(freqs, dtype=np.float64)))
    return basis @ np.asarray(coeffs, dtype=np.complex128)


def _mask_for(img, reduce: str, threshold: int, invert: bool, levels: int):
    if reduce == "edges":
        return st.edge_mask(img, thickness=2)
    if reduce == "posterize":
        masks = st.posterize_masks(img, levels=levels, invert=invert)
        return masks[0] if masks else st.mask_from_image(img, threshold, invert)
    return st.mask_from_image(img, threshold=threshold, invert=invert)


def image_to_formula(img, reduce: str = "silhouette", n_harmonics: int = 60,
                     max_side: int = 360, threshold: int = 128,
                     invert: bool = False, levels: int = 3,
                     min_perimeter: float = 24.0, max_contours: int = 12) -> dict:
    """Recover a Fourier-epicycle formula (dict) from a raster image."""
    mask = _mask_for(img, reduce, threshold, invert, levels)
    mask = st._downscale(np.asarray(mask, dtype=bool), max_side)
    # pad with a false border so shapes touching the edge still close into an
    # ordered loop (otherwise marching squares yields broken, unfittable arcs).
    mask = np.pad(mask, 2, mode="constant", constant_values=False)
    h, w = mask.shape
    contours = st.marching_squares(mask.astype(float), 0.5)
    # keep the longest contours (skip specks)
    scored = []
    for c in contours:
        cc = np.asarray(c, dtype=np.float64)
        per = np.sqrt((np.diff(np.vstack([cc, cc[0]]), axis=0) ** 2)
                      .sum(1)).sum()
        if per >= min_perimeter:
            scored.append((per, c))
    scored.sort(key=lambda s: -s[0])
    out = []
    for _, c in scored[:max_contours]:
        fit = fourier_fit(c, n_harmonics=n_harmonics)
        if fit is None:
            continue
        freqs, coeffs = fit
        out.append({"freqs": [int(f) for f in freqs],
                    "coeffs": [[float(z.real), float(z.imag)] for z in coeffs]})
    return {"type": "fourier-epicycles", "height": int(h), "width": int(w),
            "n_harmonics": int(n_harmonics), "contours": out}


# ------------------------------------------------------------ regeneration ----

def _contour_arrays(c):
    return np.asarray(c["freqs"], dtype=int), \
        np.asarray([complex(re, im) for re, im in c["coeffs"]],
                   dtype=np.complex128)


def formula_to_mask(formula: dict, size: Optional[int] = None,
                    line_width: int = 4, samples: int = 2400) -> np.ndarray:
    """Regenerate a thick-stroke boolean mask from a Fourier formula."""
    h, w = formula["height"], formula["width"]
    scale = 1.0 if size is None else size / max(h, w)
    sh, sw = max(2, int(round(h * scale))), max(2, int(round(w * scale)))
    mask = np.zeros((sh, sw), dtype=bool)
    for c in formula["contours"]:
        freqs, coeffs = _contour_arrays(c)
        z = fourier_eval(freqs, coeffs, samples) * scale
        xs, ys = z.real, z.imag
        for k in range(len(z)):
            x0, y0 = xs[k], ys[k]
            x1, y1 = xs[(k + 1) % len(z)], ys[(k + 1) % len(z)]
            st._stamp_segment(mask, (y0, x0), (y1, x1), line_width)
    return mask


# ---------------------------------------------------------------- storage ----

def save_formula(formula: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(formula, f, indent=1)


def load_formula(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def formula_equation(formula: dict, top: int = 4) -> str:
    """Human-readable summary: z(t)=Σ c_n e^{int} + dominant terms per contour."""
    lines = [f"z(t) = Σ c_n · e^(i·n·t)   "
             f"[{len(formula['contours'])} contour(s), "
             f"|n| ≤ {formula['n_harmonics']}, canvas "
             f"{formula['width']}×{formula['height']}]"]
    for ci, c in enumerate(formula["contours"]):
        freqs, coeffs = _contour_arrays(c)
        order = np.argsort(-np.abs(coeffs))[:top]
        terms = ", ".join(
            f"c[{freqs[i]:+d}]={abs(coeffs[i]):.1f}∠{np.degrees(np.angle(coeffs[i])):.0f}°"
            for i in order)
        lines.append(f"  contour {ci}: {len(freqs)} terms — {terms}")
    return "\n".join(lines)


# ------------------------------------------------------------- variations ----

def stylize(formula: dict, n_harmonics: int) -> dict:
    """Drop to |n| ≤ n_harmonics → a more abstract version of the same theme."""
    out = {**formula, "n_harmonics": int(n_harmonics), "contours": []}
    for c in formula["contours"]:
        freqs, coeffs = _contour_arrays(c)
        keep = np.abs(freqs) <= n_harmonics
        out["contours"].append(
            {"freqs": [int(f) for f in freqs[keep]],
             "coeffs": [[z.real, z.imag] for z in coeffs[keep]]})
    return out


def modulate(formula: dict, amp: float = 0.06, seed: int = 0) -> dict:
    """Jitter non-DC coefficients → an organic one-off variant of the motif."""
    rng = np.random.default_rng(seed)
    out = {**formula, "contours": []}
    for c in formula["contours"]:
        freqs, coeffs = _contour_arrays(c)
        mag = np.abs(coeffs)
        noise = (rng.standard_normal(len(coeffs))
                 + 1j * rng.standard_normal(len(coeffs)))
        pert = coeffs + amp * mag * noise * (freqs != 0)
        out["contours"].append(
            {"freqs": [int(f) for f in freqs],
             "coeffs": [[z.real, z.imag] for z in pert]})
    return out


def kaleidoscope(formula: dict, folds: int = 6) -> dict:
    """Overlay `folds` copies rotated about each contour's centroid (rosette)."""
    out = {**formula, "contours": []}
    for c in formula["contours"]:
        freqs, coeffs = _contour_arrays(c)
        for k in range(folds):
            th = 2 * np.pi * k / folds
            rot = coeffs * np.where(freqs == 0, 1.0, np.exp(1j * th))
            out["contours"].append(
                {"freqs": [int(f) for f in freqs],
                 "coeffs": [[z.real, z.imag] for z in rot]})
    return out


def _align(fa_c, fb_c):
    """Align two contours onto a common frequency set (zero-padded)."""
    fa, ca = _contour_arrays(fa_c)
    fb, cb = _contour_arrays(fb_c)
    freqs = np.array(sorted(set(fa.tolist()) | set(fb.tolist())), dtype=int)
    da = {int(f): z for f, z in zip(fa, ca)}
    db = {int(f): z for f, z in zip(fb, cb)}
    a = np.array([da.get(int(f), 0j) for f in freqs])
    b = np.array([db.get(int(f), 0j) for f in freqs])
    return freqs, a, b


def morph(fa: dict, fb: dict, t: float) -> dict:
    """Interpolate two formulas (t∈[0,1]) → a step in a transforming series."""
    out = {**fa, "contours": []}
    pairs = zip(fa["contours"], fb["contours"])
    for ca, cb in pairs:
        freqs, a, b = _align(ca, cb)
        z = (1 - t) * a + t * b
        out["contours"].append(
            {"freqs": [int(f) for f in freqs],
             "coeffs": [[zz.real, zz.imag] for zz in z]})
    return out
