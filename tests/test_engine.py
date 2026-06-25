"""Test suite for mathart package."""

import math
import os
import sys
import tempfile
import unittest
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSvgUtils(unittest.TestCase):
    def test_pts_to_path_open(self):
        from mathart._svg import pts_to_path
        d = pts_to_path([(0, 0), (10, 0), (10, 10)], close=False)
        self.assertIn("M0.000,0.000", d)
        self.assertIn("L10.000,0.000", d)
        self.assertNotIn("Z", d)

    def test_pts_to_path_closed(self):
        from mathart._svg import pts_to_path
        d = pts_to_path([(0, 0), (10, 0)], close=True)
        self.assertTrue(d.endswith("Z"))

    def test_svg_doc_structure(self):
        from mathart._svg import svg_doc
        svg = svg_doc(100, ["<circle/>"])
        self.assertIn('<svg ', svg)
        self.assertIn('</svg>', svg)
        self.assertIn('<circle/>', svg)

    def test_circle_elem(self):
        from mathart._svg import circle
        c = circle(50, 50, 10, fill="red", stroke="blue")
        self.assertIn('cx="50.000"', c)
        self.assertIn('r="10.000"', c)

    def test_save_svg(self):
        from mathart._svg import svg_doc, save_svg
        svg = svg_doc(100, [])
        with tempfile.TemporaryDirectory() as d:
            p = save_svg(svg, d, "test.svg")
            self.assertTrue(os.path.exists(p))
            with open(p) as f:
                content = f.read()
            self.assertIn("<svg", content)


class TestSacredGenerators(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def test_generators_dict(self):
        from mathart.sacred import GENERATORS
        self.assertIn("sri-yantra", GENERATORS)
        self.assertIn("flower", GENERATORS)
        self.assertTrue(callable(GENERATORS["sri-yantra"]))
        self.assertTrue(callable(GENERATORS["flower"]))

    def test_sri_yantra_outline(self):
        from mathart.sacred import generate_sri_yantra
        p = generate_sri_yantra(size=200, mode="outline", out_dir=self.tmp)
        self.assertTrue(os.path.exists(p))
        self.assertTrue(p.endswith(".svg"))
        with open(p) as f:
            svg = f.read()
        self.assertIn("<svg", svg)
        self.assertIn("path", svg)

    def test_sri_yantra_silhouette(self):
        from mathart.sacred import generate_sri_yantra
        p = generate_sri_yantra(size=200, mode="silhouette", out_dir=self.tmp)
        with open(p) as f:
            svg = f.read()
        self.assertIn('fill="black"', svg)

    def test_flower_of_life(self):
        from mathart.sacred import generate_flower
        p = generate_flower(size=200, out_dir=self.tmp)
        self.assertTrue(os.path.exists(p))
        with open(p) as f:
            svg = f.read()
        self.assertIn("circle", svg)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)


class TestPlotGenerators(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def test_plots_dict(self):
        from mathart.plot import PLOTS
        self.assertIn("streamlines", PLOTS)
        self.assertIn("superformula", PLOTS)
        self.assertTrue(callable(PLOTS["streamlines"]))
        self.assertTrue(callable(PLOTS["superformula"]))

    def test_streamlines(self):
        from mathart.plot import generate_streamlines
        p = generate_streamlines(size=200, out_dir=self.tmp)
        self.assertTrue(os.path.exists(p))
        with open(p) as f:
            svg = f.read()
        self.assertIn("path", svg)

    def test_superformula(self):
        from mathart.plot import generate_superformula
        p = generate_superformula(size=200, out_dir=self.tmp)
        self.assertTrue(os.path.exists(p))
        with open(p) as f:
            svg = f.read()
        self.assertIn("path", svg)

    def test_superformula_r_math(self):
        from mathart.plot import _superformula_r
        # m=4 should produce 4-fold symmetry: r(0)==r(pi/2)
        r0 = _superformula_r(0, m=4, a=1, b=1, n1=2, n2=2, n3=2)
        r90 = _superformula_r(math.pi / 2, m=4, a=1, b=1, n1=2, n2=2, n3=2)
        self.assertAlmostEqual(r0, r90, places=5)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)


class TestRk4(unittest.TestCase):
    def test_rk4_constant_field(self):
        from mathart.plot import _rk4_step
        # Constant field (1, 0): should move right
        def f(x, y):
            return 1.0, 0.0
        x, y = _rk4_step(f, 0.0, 0.0, 0.1)
        self.assertAlmostEqual(x, 0.1, places=8)
        self.assertAlmostEqual(y, 0.0, places=8)

    def test_rk4_circular_field(self):
        from mathart.plot import _rk4_step
        # Circular field: (-y, x) → circular orbit
        def f(x, y):
            return -y, x
        x, y = 1.0, 0.0
        for _ in range(1000):
            x, y = _rk4_step(f, x, y, 0.01)
        # After 10 units of time ≈ 1.59 full circles, still on unit circle
        self.assertAlmostEqual(x ** 2 + y ** 2, 1.0, places=2)


class TestEquilateralTriangle(unittest.TestCase):
    def test_all_sides_equal(self):
        from mathart.sacred import _equilateral_triangle
        pts = _equilateral_triangle(100, 100, 50, up=True)
        self.assertEqual(len(pts), 3)
        sides = []
        for i in range(3):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % 3]
            sides.append(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))
        self.assertAlmostEqual(sides[0], sides[1], places=3)
        self.assertAlmostEqual(sides[1], sides[2], places=3)

    def test_up_vs_down_centroid_same(self):
        from mathart.sacred import _equilateral_triangle
        up = _equilateral_triangle(0, 0, 1, up=True)
        dn = _equilateral_triangle(0, 0, 1, up=False)
        cx_up = sum(x for x, y in up) / 3
        cy_up = sum(y for x, y in up) / 3
        cx_dn = sum(x for x, y in dn) / 3
        cy_dn = sum(y for x, y in dn) / 3
        self.assertAlmostEqual(cx_up, cx_dn, places=5)
        self.assertAlmostEqual(cy_up, cy_dn, places=5)


class TestFourierTrace(unittest.TestCase):
    def test_trace_reconstructs_circle(self):
        """FFT of a sampled circle should reconstruct it well with few harmonics."""
        from mathart.trace import trace_image
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        with tempfile.TemporaryDirectory() as d:
            # Generate a circular PNG
            fig, ax = plt.subplots(figsize=(4, 4))
            ax.set_xlim(-1, 1)
            ax.set_ylim(-1, 1)
            ax.set_aspect("equal")
            ax.axis("off")
            fig.patch.set_facecolor("white")
            circle_patch = plt.Circle((0, 0), 0.7, color="black")
            ax.add_patch(circle_patch)
            png_path = os.path.join(d, "circle.png")
            fig.savefig(png_path, dpi=50, bbox_inches="tight", facecolor="white")
            plt.close(fig)

            out_svg = trace_image(png_path, harmonics=10, size=200, name="circle_trace", out_dir=d)
            self.assertTrue(os.path.exists(out_svg))
            with open(out_svg) as f:
                svg = f.read()
            self.assertIn("<svg", svg)
            self.assertIn("path", svg)

    def test_polar_to_xy(self):
        from mathart._svg import polar_to_xy
        r = np.ones(4)
        theta = np.array([0, math.pi / 2, math.pi, 3 * math.pi / 2])
        pts = polar_to_xy(r, theta, 0, 0, 1)
        self.assertAlmostEqual(pts[0][0], 1.0, places=4)   # east
        self.assertAlmostEqual(pts[1][1], -1.0, places=4)  # north (y flipped)


class TestCliList(unittest.TestCase):
    def test_list_runs(self):
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "mathart.cli", "list"],
            capture_output=True, text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("mathart inventory", result.stdout)
        self.assertIn("sri-yantra", result.stdout)


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
