"""Raw SVG generation helpers — no external dependencies."""

import math
import os


def svg_doc(size, elements, bg="white"):
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"'
        f' width="{size}" height="{size}" viewBox="0 0 {size} {size}">',
        f'  <rect width="{size}" height="{size}" fill="{bg}"/>',
    ]
    lines.extend(f"  {e}" for e in elements)
    lines.append("</svg>")
    return "\n".join(lines)


def attrs_str(**kw):
    parts = []
    for k, v in kw.items():
        k = k.replace("_", "-")
        parts.append(f'{k}="{v}"')
    return " ".join(parts)


def elem(tag, children="", **kw):
    a = attrs_str(**kw)
    if children:
        return f"<{tag} {a}>{children}</{tag}>"
    return f"<{tag} {a}/>"


def circle(cx, cy, r, **kw):
    return elem("circle", cx=f"{cx:.3f}", cy=f"{cy:.3f}", r=f"{r:.3f}", **kw)


def rect(x, y, w, h, **kw):
    return elem("rect", x=f"{x:.3f}", y=f"{y:.3f}", width=f"{w:.3f}", height=f"{h:.3f}", **kw)


def path(d, **kw):
    return elem("path", d=d, **kw)


def pts_to_path(pts, close=True):
    if not pts:
        return ""
    d = f"M{pts[0][0]:.3f},{pts[0][1]:.3f}"
    for x, y in pts[1:]:
        d += f" L{x:.3f},{y:.3f}"
    if close:
        d += " Z"
    return d


def polyline_pts(pts, closed=True):
    """Convert (x,y) list to SVG path string."""
    return pts_to_path(pts, close=closed)


def polar_to_xy(r_arr, theta_arr, cx, cy, scale):
    import numpy as np
    x = cx + scale * r_arr * np.cos(theta_arr)
    y = cy - scale * r_arr * np.sin(theta_arr)
    return list(zip(x.tolist(), y.tolist()))


def save_svg(svg_str, out_dir, filename):
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, filename)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg_str)
    return out_path
