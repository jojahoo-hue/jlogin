"""Smoke tests for the mathart engine. Run: python -m pytest tests/  (or just python tests/test_engine.py)"""

import numpy as np

from mathart import Canvas, F, render_rgb, render_set, clip255
from mathart import primitives as P
from mathart.works import REGISTRY


def test_canvas_grid_shape_and_mapping():
    c = Canvas.yeganeh(2000, 1200, 600)
    X, Y = c.grid()
    assert X.shape == (1200, 2000) and Y.shape == (1200, 2000)
    # forest mapping: x=(m-1000)/600 -> at m=1000 (index 999), x≈0
    assert abs(X[0, 999] - 0.0) < 1e-9
    # y=(601-n)/600 -> at n=1 (index 0), y=600/600=1.0
    assert abs(Y[0, 0] - 1.0) < 1e-9


def test_intensity_range():
    x = np.linspace(-1, 2, 1000)
    v = F(x)
    assert v.min() >= 0 and v.max() <= 255


def test_primitives_bounded():
    x = np.linspace(-5, 5, 200)
    assert np.all((P.double_exp(x) >= 0) & (P.double_exp(x) <= 1))
    assert np.all((P.arctan_env(x) >= 0) & (P.arctan_env(x) <= 1))
    assert np.all((P.clamp01(x) >= 0) & (P.clamp01(x) <= 1))


def test_stack_operators():
    x = np.ones((4, 4))
    assert np.allclose(P.stack_sum(lambda s: x * s, 1, 3), x * 6)
    assert np.allclose(P.stack_product(lambda s: x * s, 1, 3), x * 6)


def test_renderers_produce_images():
    c = Canvas.yeganeh(40, 30, 15)
    img = render_rgb(c, lambda X, Y: 100 + 0 * X, lambda X, Y: X * 0 + 50,
                     lambda X, Y: X * 0 + 200, intensity=clip255)
    assert img.size == (40, 30)
    img2 = render_set(c, lambda X, Y: 1 - X**2 - Y**2)
    assert img2.size == (40, 30)


def test_shapes_fields_and_masks():
    from mathart import shapes as S
    g = np.linspace(-1, 1, 50)
    X, Y = np.meshgrid(g, g)
    assert (S.ellipse(X, Y, 0, 0, 0.5, 0.5) > 0).any()      # has interior
    assert (S.capsule(X, Y, -0.5, 0, 0.5, 0, 0.1) > 0).any()
    bm = S.bird(X, Y, 0, 0, 0.5)
    assert bm.min() >= 0 and bm.max() <= 1
    fm = S.fir(X, Y, 0, -1, 1.5, 0.4)
    assert fm.min() >= 0 and fm.max() <= 1


def test_all_registered_works_render_small():
    for name, fn in REGISTRY.items():
        img = fn(width=120, height=90)
        assert img.size == (120, 90), name


def test_no_registered_work_is_dead():
    from mathart.validate_work import inspect
    for name in REGISTRY:
        img = REGISTRY[name](width=160)
        ok, reason, _ = inspect(img)
        assert ok, f"{name}: {reason}"


def test_inspect_flags_black_and_flat():
    from PIL import Image
    from mathart.validate_work import inspect
    black = Image.fromarray(np.zeros((20, 20, 3), np.uint8))
    flat = Image.fromarray(np.full((20, 20, 3), 255, np.uint8))
    good = Image.fromarray((np.indices((20, 20))[0] * 12 % 256)
                           .astype(np.uint8)[..., None].repeat(3, -1))
    assert inspect(black)[0] is False
    assert inspect(flat)[0] is False
    assert inspect(good)[0] is True


def test_stencil_vectorises_square_and_hole():
    from mathart import stencil as st
    sq = np.zeros((20, 20), bool); sq[5:15, 5:15] = True
    d = st.contours_to_d(st.marching_squares(sq.astype(float), 0.5))
    assert d.count("M") == 1, "solid square -> 1 subpath"
    holed = np.zeros((30, 30), bool); holed[5:25, 5:25] = True
    holed[12:18, 12:18] = False
    d2 = st.contours_to_d(st.marching_squares(holed.astype(float), 0.5))
    assert d2.count("M") == 2, "square with hole -> outer + hole"


def test_stencil_svg_is_wellformed():
    import xml.dom.minidom as M
    from mathart import stencil as st
    sq = np.zeros((40, 40), bool); sq[8:32, 8:32] = True
    svg = st.silhouette_svg(sq)
    doc = M.parseString(svg)                       # raises if malformed
    assert doc.getElementsByTagName("path"), "svg has a path"


def test_negative_stencil_bridges_islands():
    from mathart import stencil as st
    # frame with two separate voids that isolate a material island
    h = w = 60
    motif = np.zeros((h, w), bool)
    motif[10:50, 28] = True            # a thin wall splitting the inside
    frame = np.zeros((h, w), bool); frame[6:54, 6:54] = True
    material = frame & ~motif
    n_before = st._label(material)[1]
    bridged = st._add_bridges(material, 4.0)
    assert st._label(bridged)[1] == 1, "everything tied into one piece"
    assert n_before >= 1


def test_sacred_wheel_mask_nonempty():
    from mathart import sacred as sc, stencil as st
    m = sc.wheel_base12_mask(size=300, cs=3, line_width=4)
    assert m.any() and not m.all(), "wheel has strokes and gaps"
    svg = st.silhouette_svg(m)
    assert "<path" in svg and svg.count("M") >= 1


def test_sacred_generators_nonempty():
    import xml.dom.minidom as M
    from mathart import sacred as sc, stencil as st
    for name in ("flower", "metatron", "mandala",
                 "spiral", "enneagram", "sri-yantra"):
        m = sc.GENERATORS[name](size=300)
        assert m.any() and not m.all(), f"{name}: strokes and gaps"
        svg = st.silhouette_svg(m)
        M.parseString(svg)                         # well-formed XML
        assert svg.count("M") >= 2, f"{name}: multiple contours"


if __name__ == "__main__":
    for name, obj in list(globals().items()):
        if name.startswith("test_") and callable(obj):
            obj()
            print("PASS", name)
    print("all tests passed")
