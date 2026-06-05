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
    add_stencil_opts(s)

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
        mask = st.mask_from_image(img, threshold=args.threshold,
                                  invert=args.invert)
        svg = _to_svg(mask, args.mode, args)
        path = _write_svg(svg, args.out, f"{args.work}-{args.mode}")
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
