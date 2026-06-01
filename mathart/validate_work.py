"""Guard-rail: render every work as a thumbnail and flag dead frames.

When Claude Code generates works autonomously, the two silent failure modes are
an entirely black frame (channels collapsed to ~0, or a double-exponential read
wrong) and a flat/empty frame (a set whose field is never positive, so only the
background shows). Both render without raising, so the eye is the only check —
this module replaces the eye.

  python -m mathart.validate_work              # validate all works
  python -m mathart.validate_work horse forest # validate a subset
  python -m mathart.validate_work --out gallery/thumbs   # also dump thumbnails

Exit code is non-zero if any work fails, so it doubles as a CI / autonomy gate.
"""

from __future__ import annotations

import argparse
import os
import sys

import numpy as np

from .works import REGISTRY

# A frame is "black" if even its brightest pixel is near zero.
BLACK_MAX = 8.0
# A frame is "flat" (empty / uniform) if there is essentially no variation.
FLAT_STD = 2.0


def inspect(img):
    """Return (ok, reason, stats) for a rendered PIL image."""
    arr = np.asarray(img, dtype=np.float64)
    mx = float(arr.max())
    sd = float(arr.std())
    if mx < BLACK_MAX:
        return False, "all black", (mx, sd)
    if sd < FLAT_STD:
        return False, "flat / empty (no content)", (mx, sd)
    return True, "ok", (mx, sd)


def validate(names, size=160, out=None):
    if out:
        os.makedirs(out, exist_ok=True)

    width = size
    failures = []
    for name in names:
        try:
            img = REGISTRY[name](width=width)
        except TypeError:
            # Work doesn't accept width/height -> render at native size.
            img = REGISTRY[name]()
        except Exception as exc:  # noqa: BLE001 - a crash is also a failure
            print(f"FAIL  {name:<16} raised {type(exc).__name__}: {exc}")
            failures.append(name)
            continue

        ok, reason, (mx, sd) = inspect(img)
        flag = "ok  " if ok else "FAIL"
        print(f"{flag}  {name:<16} max={mx:6.1f} std={sd:6.1f}  {reason}")
        if not ok:
            failures.append(name)
        if out:
            img.save(os.path.join(out, f"{name}.png"))

    print()
    if failures:
        print(f"{len(failures)} of {len(names)} failed: {', '.join(failures)}")
    else:
        print(f"all {len(names)} works passed")
    return failures


def main(argv=None):
    parser = argparse.ArgumentParser(prog="mathart.validate_work")
    parser.add_argument(
        "works", nargs="*",
        help=f"works to validate (default: all). choices: {', '.join(sorted(REGISTRY))}",
    )
    parser.add_argument("--size", type=int, default=160,
                        help="thumbnail width in px (default: 160)")
    parser.add_argument("--out", default=None,
                        help="directory to save thumbnails (default: none)")
    args = parser.parse_args(argv)

    unknown = [w for w in args.works if w not in REGISTRY]
    if unknown:
        parser.error(f"unknown work(s): {', '.join(unknown)}. "
                     f"choices: {', '.join(sorted(REGISTRY))}")

    names = args.works or sorted(REGISTRY)
    failures = validate(names, size=args.size, out=args.out)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
