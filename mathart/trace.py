"""Image → Fourier contour trace → SVG reconstruction (core feature)."""

import os
import math
import numpy as np
from mathart._svg import svg_doc, path, save_svg


def _load_grayscale(img_path):
    """Load image as float numpy array in [0,1]. Uses matplotlib (no extra dep)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.image as mpimg
    img = mpimg.imread(img_path)
    if img.dtype == np.uint8:
        img = img.astype(float) / 255.0
    if img.ndim == 3:
        # Convert RGB/RGBA to luminance
        weights = np.array([0.2126, 0.7152, 0.0722])
        gray = np.dot(img[..., :3], weights)
    else:
        gray = img
    return gray


def _extract_contour(gray, threshold=0.5):
    """Find the largest foreground contour using boundary tracing."""
    # Binarize: foreground = dark pixels (shape is black on white)
    binary = (gray < threshold).astype(np.uint8)

    # Simple border-following: find boundary pixels
    rows, cols = np.where(binary == 1)
    if len(rows) == 0:
        # Try inverted
        binary = (gray >= threshold).astype(np.uint8)
        rows, cols = np.where(binary == 1)
    if len(rows) == 0:
        raise ValueError("No foreground pixels found in image")

    # Compute convex hull-like contour using angle-based sorting from centroid
    cy = rows.mean()
    cx = cols.mean()
    dr = rows - cy
    dc = cols - cx
    angles = np.arctan2(dr, dc)
    radii = np.sqrt(dr ** 2 + dc ** 2)

    # For each angle bin, keep outermost pixel
    n_bins = 1024
    bin_edges = np.linspace(-math.pi, math.pi, n_bins + 1)
    bin_idx = np.digitize(angles, bin_edges[:-1]) - 1
    bin_idx = np.clip(bin_idx, 0, n_bins - 1)

    contour_r = np.zeros(n_bins)
    contour_c = np.zeros(n_bins)
    filled = np.zeros(n_bins, dtype=bool)

    for i in range(len(rows)):
        b = bin_idx[i]
        if not filled[b] or radii[i] > math.sqrt((contour_r[b] - cy) ** 2 + (contour_c[b] - cx) ** 2):
            contour_r[b] = rows[i]
            contour_c[b] = cols[i]
            filled[b] = True

    # Interpolate missing bins
    filled_bins = np.where(filled)[0]
    if len(filled_bins) < 3:
        raise ValueError("Not enough contour points extracted")
    contour_r[~filled] = np.interp(
        np.where(~filled)[0], filled_bins, contour_r[filled_bins]
    )
    contour_c[~filled] = np.interp(
        np.where(~filled)[0], filled_bins, contour_c[filled_bins]
    )

    # Order by angle (already in bin order -pi..pi)
    xs = contour_c
    ys = contour_r
    return xs, ys, cx, cy


def trace_image(img_path, harmonics=60, size=800, name="traced", out_dir="."):
    """
    Load an image, extract its contour, approximate with N Fourier harmonics,
    and write an SVG of the reconstructed path.
    """
    gray = _load_grayscale(img_path)
    h_img, w_img = gray.shape

    xs, ys, cx_img, cy_img = _extract_contour(gray)

    # Centre + normalise contour to [-1, 1]
    xs_n = (xs - cx_img) / (max(w_img, h_img) / 2)
    ys_n = (ys - cy_img) / (max(w_img, h_img) / 2)

    # Complex signal
    z = xs_n + 1j * ys_n

    # FFT
    Z = np.fft.fft(z)
    N = len(Z)

    # Keep strongest `harmonics` frequency components (keep DC + top N pairs)
    freqs = np.fft.fftfreq(N) * N  # integer freq indices
    magnitudes = np.abs(Z)
    top_idx = np.argsort(-magnitudes)[:harmonics]
    Z_filtered = np.zeros_like(Z)
    Z_filtered[top_idx] = Z[top_idx]

    # Reconstruct
    z_rec = np.fft.ifft(Z_filtered)

    # Map to SVG canvas
    cx_svg = cy_svg = size / 2
    margin = size * 0.08
    draw_r = size / 2 - margin

    x_svg = cx_svg + z_rec.real * draw_r
    y_svg = cy_svg + z_rec.imag * draw_r

    pts = list(zip(x_svg.tolist(), y_svg.tolist()))

    elems = []
    d = "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts) + " Z"
    elems.append(path(d, fill="none", stroke="#1a1a1a",
                       stroke_width=f"{max(1.5, size * 0.002):.2f}"))

    # Annotate with harmonic count
    font_size = max(14, size // 60)
    elems.append(
        f'<text x="{size * 0.02:.0f}" y="{size - size * 0.02:.0f}" '
        f'font-family="monospace" font-size="{font_size}" fill="#888">'
        f'Fourier trace · {harmonics} harmonics</text>'
    )

    svg = svg_doc(size, elems, bg="white")
    os.makedirs(out_dir, exist_ok=True)
    return save_svg(svg, out_dir, f"{name}.svg")
