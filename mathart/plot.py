"""Matplotlib-backed "graphical scribes": rich parametric line-art → mask.

Where `mathart.sacred` rasterises thick strokes by hand, this module borrows
matplotlib's anti-aliased renderer to draw dense, organic curves (harmonograph,
spirograph, Lissajous, polar roses) and hands back the same boolean **mask** the
stencil pipeline consumes. So every plot here can become a Cricut SVG pochoir
exactly like a sacred motif.

matplotlib is an OPTIONAL dependency — importing this module without it raises a
clear message rather than failing at package import time.
"""

from __future__ import annotations

import numpy as np

try:
    import matplotlib
    matplotlib.use("Agg")                      # headless raster backend
    import matplotlib.pyplot as plt
    _HAVE_MPL = True
except Exception:                               # pragma: no cover
    _HAVE_MPL = False


def _require_mpl() -> None:
    if not _HAVE_MPL:
        raise RuntimeError(
            "matplotlib is required for mathart.plot — install it with "
            "`pip install matplotlib` (it is an optional extra)."
        )


def _new_fig(size: int):
    dpi = 100
    fig = plt.figure(figsize=(size / dpi, size / dpi), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    ax.set_xlim(-1.05, 1.05)
    ax.set_ylim(-1.05, 1.05)
    ax.set_aspect("equal")
    return fig, ax


def _fig_to_mask(fig, size: int) -> np.ndarray:
    """Rasterise a figure to a boolean mask (inked pixels = True)."""
    fig.canvas.draw()
    w, h = fig.canvas.get_width_height()
    buf = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8)
    rgba = buf.reshape(h, w, 4)
    plt.close(fig)
    lum = rgba[..., :3].mean(axis=2)
    mask = lum < 200                            # anything darker than near-white
    if mask.shape != (size, size):              # safety resample to square
        from PIL import Image
        mask = np.asarray(
            Image.fromarray((mask * 255).astype("uint8")).resize((size, size)),
            dtype=np.uint8) > 127
    return mask


def harmonograph_mask(size: int = 700, line_width: float = 1.4,
                      f1: float = 3.001, f2: float = 2.0,
                      f3: float = 3.0, f4: float = 2.002,
                      decay: float = 0.0042, steps: int = 12000) -> np.ndarray:
    """Damped two-pendulum harmonograph — dense Lissajous-like ribbon."""
    _require_mpl()
    t = np.linspace(0, 60, steps)
    e = np.exp(-decay * t)
    x = e * (np.sin(f1 * t + 0.3) + np.sin(f2 * t))
    y = e * (np.sin(f3 * t) + np.sin(f4 * t + 1.1))
    x /= np.abs(x).max() + 1e-9
    y /= np.abs(y).max() + 1e-9
    fig, ax = _new_fig(size)
    ax.plot(x, y, color="black", lw=line_width, solid_capstyle="round")
    return _fig_to_mask(fig, size)


def spirograph_mask(size: int = 700, line_width: float = 1.4,
                    R: float = 1.0, r: float = 0.34, d: float = 0.6,
                    turns: int = 50, steps: int = 8000) -> np.ndarray:
    """Hypotrochoid (spirograph) — classic gear-rosette."""
    _require_mpl()
    t = np.linspace(0, 2 * np.pi * turns, steps)
    k = (R - r) / r
    x = (R - r) * np.cos(t) + d * np.cos(k * t)
    y = (R - r) * np.sin(t) - d * np.sin(k * t)
    m = max(np.abs(x).max(), np.abs(y).max()) + 1e-9
    fig, ax = _new_fig(size)
    ax.plot(x / m, y / m, color="black", lw=line_width)
    return _fig_to_mask(fig, size)


def lissajous_mask(size: int = 700, line_width: float = 1.8,
                   a: int = 5, b: int = 4, delta: float = np.pi / 2,
                   layers: int = 6, steps: int = 4000) -> np.ndarray:
    """Stacked Lissajous curves with a slow phase drift between layers."""
    _require_mpl()
    t = np.linspace(0, 2 * np.pi, steps)
    fig, ax = _new_fig(size)
    for i in range(layers):
        ph = delta + i * np.pi / (layers * 3)
        s = 1 - 0.11 * i
        ax.plot(s * np.sin(a * t + ph), s * np.sin(b * t),
                color="black", lw=line_width)
    return _fig_to_mask(fig, size)


def rose_mask(size: int = 700, line_width: float = 1.8,
              k: float = 7.0, layers: int = 3, steps: int = 4000) -> np.ndarray:
    """Maurer-rose / polar rose r=cos(k·θ) at a few scales."""
    _require_mpl()
    t = np.linspace(0, 2 * np.pi * 1, steps)
    fig, ax = _new_fig(size)
    for i in range(layers):
        s = 1 - 0.18 * i
        r = np.cos((k + i) * t)
        ax.plot(s * r * np.cos(t), s * r * np.sin(t),
                color="black", lw=line_width)
    return _fig_to_mask(fig, size)


def phyllotaxis_mask(size: int = 700, line_width: float = 0.0,
                     n: int = 1400, dot: float = 4.0) -> np.ndarray:
    """Vogel sunflower phyllotaxis — golden-angle seed spiral (filled dots)."""
    _require_mpl()
    i = np.arange(n)
    golden = np.pi * (3 - np.sqrt(5))
    r = np.sqrt(i / n)
    a = i * golden
    x, y = r * np.cos(a), r * np.sin(a)
    fig, ax = _new_fig(size)
    ax.scatter(x, y, s=dot * (1 - 0.4 * r), c="black")
    return _fig_to_mask(fig, size)


def superformula_mask(size: int = 700, line_width: float = 1.8,
                      m: float = 7, n1: float = 3.0, n2: float = 4.0,
                      n3: float = 10.0, layers: int = 4,
                      steps: int = 4000) -> np.ndarray:
    """Gielis superformula — organic nested star/petal shapes."""
    _require_mpl()
    t = np.linspace(0, 2 * np.pi, steps)
    fig, ax = _new_fig(size)
    for i in range(layers):
        r = (np.abs(np.cos(m * t / 4)) ** n2
             + np.abs(np.sin(m * t / 4)) ** n3) ** (-1 / n1)
        r = r / (np.abs(r).max() + 1e-9) * (1 - 0.16 * i)
        ax.plot(r * np.cos(t), r * np.sin(t), color="black", lw=line_width)
    return _fig_to_mask(fig, size)


def streamlines_mask(size: int = 700, line_width: float = 1.0,
                     a: float = 1.3, b: float = 2.0,
                     density: float = 1.6, grid: int = 220) -> np.ndarray:
    """Streamlines of a curl-like vector field — flowing MATLAB-style scribe."""
    _require_mpl()
    g = np.linspace(-1, 1, grid)
    X, Y = np.meshgrid(g, g)
    U = np.sin(a * np.pi * Y) + 0.6 * np.cos(b * np.pi * X)
    V = np.sin(b * np.pi * X) - 0.6 * np.cos(a * np.pi * Y)
    fig, ax = _new_fig(size)
    ax.streamplot(X, Y, U, V, color="black", linewidth=line_width,
                  density=density, arrowstyle="-")
    return _fig_to_mask(fig, size)


def attractor_mask(size: int = 700, line_width: float = 0.0,
                   a: float = 1.641, b: float = 1.902,
                   c: float = 0.316, d: float = 1.525,
                   n: int = 120000) -> np.ndarray:
    """De Jong strange attractor — dense organic point cloud."""
    _require_mpl()
    x = y = 0.1
    xs = np.empty(n)
    ys = np.empty(n)
    for i in range(n):
        x, y = (np.sin(a * y) - np.cos(b * x),
                np.sin(c * x) - np.cos(d * y))
        xs[i], ys[i] = x, y
    m = max(np.abs(xs).max(), np.abs(ys).max()) + 1e-9
    fig, ax = _new_fig(size)
    ax.scatter(xs / m, ys / m, s=0.05, c="black", marker=".", linewidths=0)
    return _fig_to_mask(fig, size)


PLOTS = {
    "harmonograph": harmonograph_mask,
    "spirograph": spirograph_mask,
    "lissajous": lissajous_mask,
    "rose": rose_mask,
    "phyllotaxis": phyllotaxis_mask,
    "superformula": superformula_mask,
    "streamlines": streamlines_mask,
    "attractor": attractor_mask,
}
