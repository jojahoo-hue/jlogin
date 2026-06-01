# mathart — formula-driven generative art (Yeganeh-style)

Each image is computed **per pixel from a mathematical formula** — no brush, no
canvas painting. This repo turns that idea into a small, reusable engine so you
(or Claude Code) can compose new works from a shared vocabulary instead of
re-deriving pages of symbols.

## The two families

| Family | Image is… | Renderer | Example |
|---|---|---|---|
| **Color** | `rgb(F(R), F(G), F(B))` per pixel | `render_rgb` | forest, turbines |
| **Set** | the region `{(x, y) \| T(x, y) > 0}` | `render_set` | horse |

## Architecture

```
mathart/
  canvas.py        # pixel grid (m,n) -> coordinates (x,y), fully vectorized
  intensity.py     # F(x): the shared 0..255 clamp used by every color work
  primitives.py    # THE CORE: the reusable math vocabulary (see below)
  renderers/
    rgb.py         # Family 1
    inequality.py  # Family 2
  works/           # one module per artwork, each exposes render(...)
  cli.py           # python -m mathart.cli render <work>
gallery/           # output PNGs
```

Two design choices make it usable:

1. **Vectorized numpy.** A whole image is evaluated on the `(X, Y)` grids in one
   pass — never pixel-by-pixel Python loops (millions of calls).
2. **Named primitives.** `primitives.py` is the vocabulary the giant formulas
   are actually built from: `double_exp`, `soft_step`, `soft_window`, `bump`,
   `arctan_env`, `stack_sum` (add many objects), `stack_product` (mask/intersect
   many regions), `warp`. New art = composing these, not re-deriving them.

## Run

```bash
python -m mathart.cli list
python -m mathart.cli render forest --out gallery
python -m mathart.cli render turbines --width 1800 --height 1000
python -m mathart.cli render horse
```

## Add a new work (the Claude Code loop)

Copy `works/_template.py`, fill in the channel functions (color) or the field
`T` (set), register it in `works/__init__.py`. That's it.

- **Color work:** return raw `R, G, B`. Use `intensity=F` to match Yeganeh's
  encoding, or `intensity=clip255` for direct 0..255 colors.
- **Set work:** return one field `T`; ink goes where `T > 0`. Build shapes as a
  `np.maximum(...)` union of parts, intersect with `*`, sculpt with primitives.

## Reproducing the *exact* published pieces

The included works are original compositions using the same techniques. To
reproduce a specific Yeganeh image byte-for-byte, transcribe its published
`H_v / C / N / K / M / A …` (or `A_v / P_s / Q_s / W …`) expressions into a work
module using the primitives, set the canvas to the stated size/scale, and render
with `intensity=F`. The engine is built for exactly that substitution.
