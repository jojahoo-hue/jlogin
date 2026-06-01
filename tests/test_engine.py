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


if __name__ == "__main__":
    for name, obj in list(globals().items()):
        if name.startswith("test_") and callable(obj):
            obj()
            print("PASS", name)
    print("all tests passed")
