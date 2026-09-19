"""Mathematical plot generators: streamlines, superformula."""

import math
import numpy as np
from mathart._svg import svg_doc, path, pts_to_path, save_svg, circle


def _rk4_step(f, x, y, dt):
    k1x, k1y = f(x, y)
    k2x, k2y = f(x + 0.5 * dt * k1x, y + 0.5 * dt * k1y)
    k3x, k3y = f(x + 0.5 * dt * k2x, y + 0.5 * dt * k2y)
    k4x, k4y = f(x + dt * k3x, y + dt * k3y)
    return (
        x + dt * (k1x + 2 * k2x + 2 * k3x + k4x) / 6,
        y + dt * (k1y + 2 * k2y + 2 * k3y + k4y) / 6,
    )


def generate_streamlines(size=800, out_dir="."):
    """Streamlines of a dipole + rotation vector field."""
    stroke_w = max(1.0, size * 0.0015)
    elems = []

    # Vector field: superposition of vortices + gentle rotation
    def field(x, y):
        vx, vy = 0.0, 0.0
        vortices = [(-0.4, 0.0, 1.2), (0.4, 0.0, -1.2), (0.0, -0.4, 0.8), (0.0, 0.4, -0.8)]
        for vox, voy, strength in vortices:
            dx = x - vox
            dy = y - voy
            r2 = dx * dx + dy * dy + 0.01
            vx += strength * (-dy) / r2
            vy += strength * dx / r2
        # Add background rotation
        vx += -0.3 * y
        vy += 0.3 * x
        mag = math.sqrt(vx * vx + vy * vy) + 1e-9
        return vx / mag, vy / mag

    cx = cy = size / 2
    scale = size * 0.46

    # Seed streamlines on a grid
    palette = ["#2c3e50", "#8e44ad", "#2980b9", "#16a085", "#e74c3c", "#f39c12"]
    n_seeds = 28
    steps = 400
    dt = 0.018

    for i in range(n_seeds):
        angle = i * 2 * math.pi / n_seeds
        for radius in [0.25, 0.50, 0.78]:
            sx = radius * math.cos(angle)
            sy = radius * math.sin(angle)
            pts = [(cx + sx * scale, cy - sy * scale)]
            x, y = sx, sy
            for _ in range(steps):
                x, y = _rk4_step(field, x, y, dt)
                r = math.sqrt(x * x + y * y)
                if r > 1.05:
                    break
                pts.append((cx + x * scale, cy - y * scale))
            if len(pts) > 3:
                color = palette[i % len(palette)]
                d = pts_to_path(pts, close=False)
                elems.append(path(d, fill="none", stroke=color,
                                   stroke_width=f"{stroke_w:.2f}", opacity="0.75"))

    # Outer boundary
    elems.append(circle(cx, cy, scale, fill="none", stroke="#1a1a1a",
                         stroke_width=f"{stroke_w * 2:.2f}"))

    svg = svg_doc(size, elems, bg="#fafafa")
    return save_svg(svg, out_dir, "streamlines.svg")


def _superformula_r(theta, m, a, b, n1, n2, n3):
    """Gielis superformula."""
    t = m * theta / 4.0
    try:
        val = (abs(math.cos(t) / a) ** n2 + abs(math.sin(t) / b) ** n3) ** (1.0 / n1)
        return 1.0 / val if val != 0 else 0
    except ZeroDivisionError:
        return 0.0


def generate_superformula(size=800, out_dir="."):
    """Multiple superformula curves overlaid."""
    cx = cy = size / 2
    scale = size * 0.44
    stroke_w = max(1.5, size * 0.002)
    n_pts = 2000

    # (m, a, b, n1, n2, n3, color, opacity)
    configs = [
        (6,  1, 1, 2.0,  18,  18, "#2c3e50", "0.9"),
        (5,  1, 1, 3.0,  4.0, 7.0, "#8e44ad", "0.85"),
        (4,  1, 1, 0.5,  0.5, 4.0, "#e74c3c", "0.80"),
        (8,  1, 1, 1.0,  5.0, 5.0, "#2980b9", "0.75"),
        (3,  1, 1, 4.5,  10,  10, "#27ae60", "0.70"),
        (7,  1, 1, 2.5,  6.0, 6.0, "#e67e22", "0.65"),
        (12, 1, 1, 1.5,  2.0, 2.0, "#1abc9c", "0.60"),
    ]

    elems = []
    thetas = np.linspace(0, 2 * math.pi, n_pts + 1)

    for m, a, b, n1, n2, n3, color, opacity in configs:
        rs = np.array([_superformula_r(t, m, a, b, n1, n2, n3) for t in thetas])
        max_r = rs.max()
        if max_r == 0:
            continue
        rs /= max_r
        xs = cx + scale * rs * np.cos(thetas)
        ys = cy - scale * rs * np.sin(thetas)
        pts = list(zip(xs.tolist(), ys.tolist()))
        d = pts_to_path(pts, close=True)
        elems.append(path(d, fill="none", stroke=color,
                           stroke_width=f"{stroke_w:.2f}", opacity=opacity))

    svg = svg_doc(size, elems, bg="white")
    return save_svg(svg, out_dir, "superformula.svg")


def generate_harmonograph(size=800, out_dir="."):
    """Harmonograph: overlapping damped-pendulum Lissajous curves."""
    cx = cy = size / 2
    scale = size * 0.44
    stroke_w = max(0.8, size * 0.0012)

    configs = [
        (3, 2, 3, 2, 0, math.pi/2, math.pi/4, 0, 0.004, 0.005, 0.004, 0.003, "#2c3e50", "0.90"),
        (5, 4, 5, 4, 0, math.pi/3, math.pi/6, 0, 0.003, 0.004, 0.003, 0.004, "#8e44ad", "0.85"),
        (4, 3, 4, 3, math.pi/4, 0, 0, math.pi/4, 0.005, 0.004, 0.005, 0.003, "#2980b9", "0.80"),
        (6, 5, 6, 5, 0, math.pi/2, math.pi/3, 0, 0.004, 0.003, 0.004, 0.005, "#16a085", "0.75"),
        (7, 6, 7, 6, math.pi/5, 0, 0, math.pi/5, 0.003, 0.005, 0.004, 0.003, "#e74c3c", "0.70"),
    ]

    n_pts = 5000
    t_vals = np.linspace(0, 5000 * 0.04, n_pts)
    elems = []
    for f1, f2, f3, f4, p1, p2, p3, p4, d1, d2, d3, d4, color, opacity in configs:
        xs = (np.sin(f1 * t_vals + p1) * np.exp(-d1 * t_vals) +
              np.sin(f2 * t_vals + p2) * np.exp(-d2 * t_vals))
        ys = (np.sin(f3 * t_vals + p3) * np.exp(-d3 * t_vals) +
              np.sin(f4 * t_vals + p4) * np.exp(-d4 * t_vals))
        mx = float(np.abs(xs).max()) or 1.0
        my = float(np.abs(ys).max()) or 1.0
        pts = [(cx + x / mx * scale, cy - y / my * scale)
               for x, y in zip(xs.tolist(), ys.tolist())]
        d = pts_to_path(pts, close=False)
        elems.append(path(d, fill="none", stroke=color,
                           stroke_width=f"{stroke_w:.2f}", opacity=opacity))

    svg = svg_doc(size, elems, bg="white")
    return save_svg(svg, out_dir, "harmonograph.svg")


def generate_spirograph(size=800, out_dir="."):
    """Spirograph: overlapping hypotrochoid curves."""
    from math import gcd
    cx = cy = size / 2
    scale = size * 0.44
    stroke_w = max(0.8, size * 0.0012)

    configs = [
        (7, 3, 4.5, "#2c3e50", "0.90"),
        (5, 2, 3.0, "#8e44ad", "0.85"),
        (9, 4, 6.0, "#e74c3c", "0.80"),
        (8, 3, 5.0, "#2980b9", "0.75"),
        (6, 1, 4.5, "#27ae60", "0.70"),
        (10, 7, 3.5, "#e67e22", "0.65"),
    ]

    n_pts = 5000
    elems = []
    for R, r, d_mult, color, opacity in configs:
        d = d_mult * r
        lcm = R * r // gcd(R, r)
        t_end = 2 * math.pi * lcm / r
        t_vals = np.linspace(0, t_end, n_pts)
        ratio = (R - r) / r
        xs = (R - r) * np.cos(t_vals) + d * np.cos(ratio * t_vals)
        ys = (R - r) * np.sin(t_vals) - d * np.sin(ratio * t_vals)
        max_r = max(float(np.abs(xs).max()), float(np.abs(ys).max()), 1e-9)
        xs = xs / max_r
        ys = ys / max_r
        pts = [(cx + x * scale, cy - y * scale) for x, y in zip(xs.tolist(), ys.tolist())]
        dattr = pts_to_path(pts, close=True)
        elems.append(path(dattr, fill="none", stroke=color,
                           stroke_width=f"{stroke_w:.2f}", opacity=opacity))

    svg = svg_doc(size, elems, bg="white")
    return save_svg(svg, out_dir, "spirograph.svg")


PLOTS = {
    "streamlines": generate_streamlines,
    "superformula": generate_superformula,
    "harmonograph": generate_harmonograph,
    "spirograph": generate_spirograph,
}
