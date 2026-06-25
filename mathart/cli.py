"""mathart CLI — formula-driven generative art."""

import argparse
import sys
import os


def cmd_sacred(args):
    from mathart.sacred import GENERATORS
    name = args.name
    if name not in GENERATORS:
        print(f"Unknown sacred design '{name}'. Available: {', '.join(GENERATORS)}", file=sys.stderr)
        sys.exit(1)
    fn = GENERATORS[name]
    kwargs = {"size": args.size, "out_dir": args.out}
    if name == "sri-yantra":
        kwargs["mode"] = args.mode
    out = fn(**kwargs)
    print(f"Saved: {out}")


def cmd_plot(args):
    from mathart.plot import PLOTS
    name = args.name
    if name not in PLOTS:
        print(f"Unknown plot '{name}'. Available: {', '.join(PLOTS)}", file=sys.stderr)
        sys.exit(1)
    out = PLOTS[name](size=args.size, out_dir=args.out)
    print(f"Saved: {out}")


def cmd_render(args):
    from mathart.render import RENDERS
    name = args.name
    if name not in RENDERS:
        print(f"Unknown render target '{name}'. Available: {', '.join(RENDERS)}", file=sys.stderr)
        sys.exit(1)
    fn = RENDERS[name]
    kwargs = {"out_dir": args.out}
    if hasattr(args, "width") and args.width:
        kwargs["width"] = args.width
    out = fn(**kwargs)
    print(f"Saved: {out}")


def cmd_trace(args):
    from mathart.trace import trace_image
    out = trace_image(
        img_path=args.input,
        harmonics=args.harmonics,
        size=args.size,
        name=args.name,
        out_dir=args.out,
    )
    print(f"Saved: {out}")


def cmd_list(args):
    from mathart.sacred import GENERATORS
    from mathart.plot import PLOTS
    from mathart.render import RENDERS

    print("=== mathart inventory ===\n")
    print("Sacred designs:")
    for k in GENERATORS:
        print(f"  sacred {k}")
    print("\nPlots:")
    for k in PLOTS:
        print(f"  plot {k}")
    print("\nRender targets:")
    for k in RENDERS:
        print(f"  render {k}")
    print("\nTrace: any PNG/JPEG via FFT contour reconstruction")

    # List existing gallery artefacts
    gallery = os.path.join(os.path.dirname(os.path.dirname(__file__)), "gallery")
    if os.path.isdir(gallery):
        svgs = []
        pngs = []
        for root, dirs, files in os.walk(gallery):
            for f in files:
                fp = os.path.join(root, f)
                rel = os.path.relpath(fp, gallery)
                if f.endswith(".svg"):
                    svgs.append(rel)
                elif f.endswith(".png"):
                    pngs.append(rel)
        if svgs or pngs:
            print(f"\nGallery artefacts ({len(svgs)} SVG, {len(pngs)} PNG):")
            for p in sorted(svgs + pngs):
                print(f"  gallery/{p}")


def main():
    parser = argparse.ArgumentParser(
        prog="mathart",
        description="Formula-driven generative art for Cricut SVG stencils",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # sacred
    p_sacred = sub.add_parser("sacred", help="Generate sacred geometry SVG")
    p_sacred.add_argument("name", help="Design name (sri-yantra, flower)")
    p_sacred.add_argument("--size", type=int, default=800)
    p_sacred.add_argument("--mode", default="outline", choices=["outline", "silhouette"])
    p_sacred.add_argument("--out", default="gallery")
    p_sacred.set_defaults(func=cmd_sacred)

    # plot
    p_plot = sub.add_parser("plot", help="Generate mathematical plot SVG")
    p_plot.add_argument("name", help="Plot name (streamlines, superformula)")
    p_plot.add_argument("--size", type=int, default=800)
    p_plot.add_argument("--out", default="gallery")
    p_plot.set_defaults(func=cmd_plot)

    # render
    p_render = sub.add_parser("render", help="Render reference image as PNG")
    p_render.add_argument("name", help="Render target (horse)")
    p_render.add_argument("--width", type=int, default=1600)
    p_render.add_argument("--out", default="gallery")
    p_render.set_defaults(func=cmd_render)

    # trace
    p_trace = sub.add_parser("trace", help="Fourier-trace a PNG into SVG")
    p_trace.add_argument("input", help="Input PNG path")
    p_trace.add_argument("--harmonics", type=int, default=60)
    p_trace.add_argument("--size", type=int, default=800)
    p_trace.add_argument("--name", default="traced")
    p_trace.add_argument("--out", default="gallery")
    p_trace.set_defaults(func=cmd_trace)

    # list
    p_list = sub.add_parser("list", help="List available works and gallery artefacts")
    p_list.set_defaults(func=cmd_list)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
