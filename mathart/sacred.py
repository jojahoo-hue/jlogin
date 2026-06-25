"""Sacred geometry generators: Sri Yantra, Flower of Life."""

import math
import numpy as np
from mathart._svg import svg_doc, circle, rect, path, pts_to_path, save_svg


def _equilateral_triangle(cx, cy, r, up=True):
    """Return 3 vertices of an equilateral triangle inscribed in circle of radius r."""
    offset = 0 if up else math.pi
    return [
        (cx + r * math.sin(offset + 2 * math.pi * k / 3),
         cy - r * math.cos(offset + 2 * math.pi * k / 3))
        for k in range(3)
    ]


def generate_sri_yantra(size=800, mode="outline", out_dir="."):
    """Sri Yantra: 9 interlocking triangles, lotus petals, bhupura square."""
    cx = cy = size / 2
    stroke = "white" if mode == "silhouette" else "#1a1a1a"
    bg = "black" if mode == "silhouette" else "white"
    stroke_w = max(1.5, size * 0.0018)

    def tri_path(r, up, fill="none", sw=None):
        pts = _equilateral_triangle(cx, cy, r, up)
        d = pts_to_path(pts)
        return path(d, fill=fill, stroke=stroke, stroke_width=f"{sw or stroke_w:.2f}")

    elems = []

    # Outer bhupura (nested squares with gates)
    for frac in [0.495, 0.472, 0.450]:
        s = size * frac
        elems.append(rect(cx - s, cy - s, s * 2, s * 2,
                          fill="none", stroke=stroke, stroke_width=f"{stroke_w:.2f}"))

    # Gate notches on each side (simple T-shapes)
    gate_w = size * 0.06
    gate_h = size * 0.04
    s0 = size * 0.495
    for angle in [0, 90, 180, 270]:
        rad = math.radians(angle)
        gx = cx + s0 * math.cos(rad) - gate_w / 2
        gy = cy + s0 * math.sin(rad)
        if angle == 0:
            elems.append(rect(cx + s0, cy - gate_w / 2, gate_h, gate_w,
                               fill="none", stroke=stroke, stroke_width=f"{stroke_w:.2f}"))
        elif angle == 90:
            elems.append(rect(cx - gate_w / 2, cy + s0, gate_w, gate_h,
                               fill="none", stroke=stroke, stroke_width=f"{stroke_w:.2f}"))
        elif angle == 180:
            elems.append(rect(cx - s0 - gate_h, cy - gate_w / 2, gate_h, gate_w,
                               fill="none", stroke=stroke, stroke_width=f"{stroke_w:.2f}"))
        elif angle == 270:
            elems.append(rect(cx - gate_w / 2, cy - s0 - gate_h, gate_w, gate_h,
                               fill="none", stroke=stroke, stroke_width=f"{stroke_w:.2f}"))

    # Outer lotus rings
    for ring_r, n_petals in [(size * 0.415, 16), (size * 0.33, 8)]:
        petal_r = ring_r * 0.18
        for i in range(n_petals):
            angle = i * 2 * math.pi / n_petals
            px = cx + ring_r * math.sin(angle)
            py = cy - ring_r * math.cos(angle)
            rot_deg = math.degrees(angle)
            rx = petal_r
            ry = petal_r * 0.4
            elems.append(
                f'<ellipse cx="{px:.2f}" cy="{py:.2f}" rx="{rx:.2f}" ry="{ry:.2f}" '
                f'transform="rotate({rot_deg:.2f},{px:.2f},{py:.2f})" '
                f'fill="none" stroke="{stroke}" stroke-width="{stroke_w:.2f}"/>'
            )
        elems.append(circle(cx, cy, ring_r, fill="none", stroke=stroke,
                             stroke_width=f"{stroke_w:.2f}"))

    # Inner containment circle
    elems.append(circle(cx, cy, size * 0.27, fill="none", stroke=stroke,
                         stroke_width=f"{stroke_w:.2f}"))

    # 9 interlocking triangles
    # 4 upward (Shiva) + 5 downward (Shakti) in decreasing radii
    r_base = size * 0.255
    up_scales = [1.00, 0.80, 0.58, 0.36]
    down_scales = [0.92, 0.72, 0.54, 0.35, 0.18]

    for sc in up_scales:
        elems.append(tri_path(r_base * sc, up=True, sw=stroke_w * 1.1))
    for sc in down_scales:
        elems.append(tri_path(r_base * sc, up=False, sw=stroke_w * 1.1))

    # Central bindu
    bindu_r = size * 0.008
    elems.append(circle(cx, cy, bindu_r, fill=stroke, stroke="none"))

    svg = svg_doc(size, elems, bg=bg)
    return save_svg(svg, out_dir, "sri-yantra.svg")


def generate_flower(size=800, out_dir="."):
    """Flower of Life: hexagonal grid of overlapping circles."""
    cx = cy = size / 2
    stroke = "#1a1a1a"
    stroke_w = max(1.5, size * 0.0018)

    # Petal radius = spacing between circle centers
    r = size * 0.08
    outer_clip_r = size * 0.46

    elems = []

    # Clip path for outer boundary
    clip_id = "flower-clip"
    elems.insert(0,
        f'<defs><clipPath id="{clip_id}">'
        f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{outer_clip_r:.2f}"/>'
        f'</clipPath></defs>'
    )

    group_open = f'<g clip-path="url(#{clip_id})">'
    group_close = "</g>"

    circles = []
    # Hexagonal lattice: a1=(r,0), a2=(r/2, r*sqrt(3)/2)
    a1x, a1y = r * 2, 0.0
    a2x = r * 2 * 0.5
    a2y = r * 2 * (math.sqrt(3) / 2)

    seen = set()
    for i in range(-8, 9):
        for j in range(-8, 9):
            lx = cx + i * a1x + j * a2x
            ly = cy + i * a1y + j * a2y
            key = (round(lx, 1), round(ly, 1))
            if key in seen:
                continue
            seen.add(key)
            # Include if within clipping region + margin
            dist = math.sqrt((lx - cx) ** 2 + (ly - cy) ** 2)
            if dist <= outer_clip_r + r:
                circles.append((lx, ly))

    inner_elems = []
    for lx, ly in circles:
        inner_elems.append(
            circle(lx, ly, r, fill="none", stroke=stroke, stroke_width=f"{stroke_w:.2f}")
        )

    # Outer boundary circle
    boundary = circle(cx, cy, outer_clip_r, fill="none", stroke=stroke,
                       stroke_width=f"{stroke_w * 2:.2f}")

    full_elems = (
        [elems[0]]  # defs
        + [group_open]
        + inner_elems
        + [group_close]
        + [boundary]
    )

    svg = svg_doc(size, full_elems, bg="white")
    return save_svg(svg, out_dir, "flower.svg")


GENERATORS = {
    "sri-yantra": generate_sri_yantra,
    "flower": generate_flower,
}
