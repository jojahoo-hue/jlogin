"""Command-line interface: `python -m mathart.cli render forest --out gallery/`."""

from __future__ import annotations

import argparse
import os

from .works import REGISTRY


def main(argv=None):
    parser = argparse.ArgumentParser(prog="mathart")
    sub = parser.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("render", help="render a work to PNG")
    r.add_argument("work", choices=sorted(REGISTRY), help="which work")
    r.add_argument("--out", default="gallery", help="output directory")
    r.add_argument("--width", type=int, default=None)
    r.add_argument("--height", type=int, default=None)

    sub.add_parser("list", help="list available works")

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


if __name__ == "__main__":
    main()
