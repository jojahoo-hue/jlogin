"""Render reference images (horse etc.) as PNG using matplotlib."""

import os
import math
import numpy as np


def render_horse(width=1600, out_dir="."):
    """Generate a horse silhouette PNG using matplotlib patches."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.path import Path as MPath
    import matplotlib.patheffects as pe

    fig, ax = plt.subplots(figsize=(width / 100, width / 100), dpi=100)
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    def add_ellipse(x, y, w, h, angle=0):
        e = mpatches.Ellipse((x, y), w, h, angle=angle, color="black", zorder=2)
        ax.add_patch(e)

    def add_rect(x, y, w, h):
        r = mpatches.Rectangle((x, y), w, h, color="black", zorder=2)
        ax.add_patch(r)

    # Body
    add_ellipse(-0.08, -0.05, 1.00, 0.50, angle=-5)
    # Hindquarters bulge
    add_ellipse(-0.48, 0.02, 0.38, 0.32, angle=5)
    # Shoulder
    add_ellipse(0.28, 0.02, 0.32, 0.30, angle=-10)

    # Neck
    add_ellipse(0.45, 0.25, 0.32, 0.18, angle=55)
    # Head
    add_ellipse(0.62, 0.50, 0.32, 0.18, angle=15)
    # Muzzle
    add_ellipse(0.73, 0.46, 0.16, 0.11, angle=5)

    # Ear
    ear_verts = [(0.48, 0.72), (0.53, 0.88), (0.58, 0.72), (0.48, 0.72)]
    ear_codes = [MPath.MOVETO, MPath.LINETO, MPath.LINETO, MPath.CLOSEPOLY]
    ear_path = MPath(ear_verts, ear_codes)
    ear_patch = mpatches.PathPatch(ear_path, facecolor="black", edgecolor="black", zorder=3)
    ax.add_patch(ear_patch)

    # Legs — front
    lw = 0.065
    for lx in [0.20, 0.30]:
        add_rect(lx - lw / 2, -0.30, lw, 0.48)
        # Hoof
        add_ellipse(lx, -0.84, lw * 1.4, lw * 0.7)

    # Legs — hind
    for lx in [-0.40, -0.52]:
        add_rect(lx - lw / 2, -0.30, lw, 0.44)
        add_ellipse(lx, -0.80, lw * 1.4, lw * 0.7)

    # Tail (bezier curve rendered as thick patch)
    tail_verts = [
        (-0.63, 0.12),
        (-0.82, 0.50),
        (-0.90, 0.30),
        (-0.78, -0.10),
    ]
    tail_codes = [MPath.MOVETO, MPath.CURVE4, MPath.CURVE4, MPath.CURVE4]
    tail_path = MPath(tail_verts, tail_codes)
    tail_patch = mpatches.PathPatch(tail_path, facecolor="none", edgecolor="black",
                                    linewidth=14, capstyle="round", zorder=2)
    ax.add_patch(tail_patch)

    # Mane (along neck)
    mane_x = np.array([0.38, 0.32, 0.26, 0.22, 0.28, 0.34, 0.40])
    mane_y = np.array([0.42, 0.50, 0.56, 0.62, 0.60, 0.54, 0.48])
    ax.fill(mane_x, mane_y, color="black", zorder=3)

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "horse.png")
    fig.savefig(out_path, dpi=100, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    return out_path


RENDERS = {
    "horse": render_horse,
}
