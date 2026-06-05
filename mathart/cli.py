"""CLI: `render` to PNG, `stencil`/`sacred` to Cricut-ready SVG.

    python -m mathart.cli list
    python -m mathart.cli render forest --out gallery
    python -m mathart.cli stencil horse --mode negative --out gallery
    python -m mathart.cli sacred wheel --cs 3 --mode silhouette --out gallery
"""

from __future__ import annotations

import argparse
import os

from .works import REGISTRY


def _write_svg(svg: str, out: str, name: str) -> str:
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, f"{name}.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return path


def _to_svg(mask, mode: str, args) -> str:
    from . import stencil as st
    if mode == "negative":
        return st.negative_svg(mask, frame_margin=args.frame_margin,
                               bridge_width=args.bridge_width,
                               max_side=args.max_side)
    return st.silhouette_svg(mask, max_side=args.max_side)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="mathart")
    sub = parser.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("render", help="render a work to PNG")
    r.add_argument("work", choices=sorted(REGISTRY), help="which work")
    r.add_argument("--out", default="gallery", help="output directory")
    r.add_argument("--width", type=int, default=None)
    r.add_argument("--height", type=int, default=None)

    sub.add_parser("list", help="list available works")

    def add_stencil_opts(p):
        p.add_argument("--mode", choices=["silhouette", "negative"],
                       default="silhouette")
        p.add_argument("--out", default="gallery")
        p.add_argument("--max-side", type=int, default=360,
                       help="vectorise at this resolution (Cricut-friendly)")
        p.add_argument("--frame-margin", type=int, default=12,
                       help="[negative] frame thickness in px")
        p.add_argument("--bridge-width", type=float, default=6.0,
                       help="[negative] auto-bridge width in px")

    s = sub.add_parser("stencil", help="vectorise a work to an SVG stencil")
    s.add_argument("work", choices=sorted(REGISTRY))
    s.add_argument("--threshold", type=int, default=128,
                   help="dark<thr = motif")
    s.add_argument("--invert", action="store_true")
    s.add_argument("--width", type=int, default=600)
    s.add_argument("--reduce", choices=["threshold", "posterize", "edges"],
                   default="threshold",
                   help="how to turn the render into a mask")
    s.add_argument("--levels", type=int, default=3,
                   help="[posterize] number of tone bands")
    s.add_argument("--edge-threshold", type=float, default=0.18,
                   help="[edges] gradient cutoff (0..1)")
    add_stencil_opts(s)

    p = sub.add_parser("plot", help="matplotlib graphical scribe -> SVG stencil")
    from .plot import PLOTS
    p.add_argument("design", choices=sorted(PLOTS))
    p.add_argument("--size", type=int, default=700)
    p.add_argument("--line-width", type=float, default=1.6)
    add_stencil_opts(p)

    ai = sub.add_parser("aigen",
                        help="Nano Banana (Gemini) prompt -> SVG stencil")
    ai.add_argument("prompt", help="text description of the motif")
    ai.add_argument("--reduce", choices=["posterize", "edges"],
                    default="posterize")
    ai.add_argument("--levels", type=int, default=2)
    ai.add_argument("--edge-threshold", type=float, default=0.18)
    ai.add_argument("--name", default="aigen", help="output file stem")
    add_stencil_opts(ai)

    g = sub.add_parser("sacred", help="parametric sacred-geometry SVG stencil")
    from .sacred import GENERATORS
    g.add_argument("design", choices=sorted(GENERATORS))
    g.add_argument("--cs", type=int, default=3, help="Code Secret (wheel)")
    g.add_argument("--size", type=int, default=700)
    g.add_argument("--line-width", type=int, default=6)
    g.add_argument("--petals", type=int, default=12, help="[mandala] N-fold")
    g.add_argument("--rings", type=int, default=3,
                   help="[mandala] concentric rings")
    add_stencil_opts(g)

    args = parser.parse_args(argv)

    if args.cmd == "list":
        for name in sorted(REGISTRY):
            print(name)
        return

    if args.cmd == "render":
        kwargs = {}
        if args.width:
            kwargs["width"] = args.width
        if args.height:
            kwargs["height"] = args.height
        img = REGISTRY[args.work](**kwargs)
        os.makedirs(args.out, exist_ok=True)
        path = os.path.join(args.out, f"{args.work}.png")
        img.save(path)
        print(f"saved {path}  ({img.width}x{img.height})")
        return

    if args.cmd == "stencil":
        from . import stencil as st
        img = REGISTRY[args.work](width=args.width)
        if args.reduce == "posterize":
            masks = st.posterize_masks(img, levels=args.levels,
                                       invert=args.invert)
            for i, mask in enumerate(masks):
                svg = _to_svg(mask, args.mode, args)
                stem = f"{args.work}-{args.mode}-L{i}"
                print(f"saved {_write_svg(svg, args.out, stem)}")
            return
        if args.reduce == "edges":
            mask = st.edge_mask(img, threshold=args.edge_threshold,
                                thickness=2)
        else:
            mask = st.mask_from_image(img, threshold=args.threshold,
                                      invert=args.invert)
        svg = _to_svg(mask, args.mode, args)
        path = _write_svg(svg, args.out, f"{args.work}-{args.mode}")
        print(f"saved {path}")
        return

    if args.cmd == "plot":
        from .plot import PLOTS
        mask = PLOTS[args.design](size=args.size, line_width=args.line_width)
        svg = _to_svg(mask, args.mode, args)
        path = _write_svg(svg, args.out, f"{args.design}-{args.mode}")
        print(f"saved {path}")
        return

    if args.cmd == "aigen":
        from . import aigen
        if not aigen.available():
            parser.error(
                "Nano Banana is dormant: set GEMINI_API_KEY (or GOOGLE_API_KEY) "
                "and `pip install google-genai` to enable it.")
        mask = aigen.mask_from_prompt(args.prompt, reduce=args.reduce,
                                      levels=args.levels,
                                      edge_threshold=args.edge_threshold)
        svg = _to_svg(mask, args.mode, args)
        path = _write_svg(svg, args.out, f"{args.name}-{args.mode}")
        print(f"saved {path}")
        return

    if args.cmd == "sacred":
        from .sacred import GENERATORS
        gen = GENERATORS[args.design]
        kwargs = {"size": args.size, "line_width": args.line_width}
        if args.design == "wheel":
            kwargs["cs"] = args.cs
        elif args.design == "mandala":
            kwargs["petals"] = args.petals
            kwargs["rings"] = args.rings
        mask = gen(**kwargs)
        svg = _to_svg(mask, args.mode, args)
        path = _write_svg(svg, args.out, f"{args.design}-{args.mode}")
        print(f"saved {path}")
        return


if __name__ == "__main__":
    main()
