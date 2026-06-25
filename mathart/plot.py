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


PLOTS = {
    "streamlines": generate_streamlines,
    "superformula": generate_superformula,
}
