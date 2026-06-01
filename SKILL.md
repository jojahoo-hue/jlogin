---
name: mathart
description: >
  Create formula-driven generative art (Yeganeh-style "mathematical paintings"):
  images where every pixel's color, or membership in a set, is computed from a
  math formula — no brush, no canvas. Use this skill whenever the user wants to
  generate, design, compose, or reproduce algorithmic / mathematical / parametric
  art: pixel-formula images, trig/exponential silhouettes, generative landscapes
  or creatures, or works "in the style of Hamid Naderi Yeganeh". Trigger on
  requests like "make math art", "draw an X from equations", "render a formula
  as an image", "reproduce this Yeganeh piece", or "add a new work to mathart".
---

# mathart — formula-driven generative art

Every image is computed per pixel from a formula. This skill is the engine plus
the vocabulary to compose new works fast, without re-deriving pages of symbols.

## When to use
- The user wants an image *defined by math* (not a painting tool, not an AI image).
- Reproducing or extending a Yeganeh-style pixel formula.
- Adding/editing a work in the `mathart` package.

## Setup (once per session)
```bash
cd mathart
pip install -e . --break-system-packages      # numpy + pillow only
python -m mathart.cli list                     # forest, turbines, horse, turbines-exact
python -m mathart.cli render forest --out gallery
```
After rendering, ALWAYS open the PNG and inspect it; iterate visually.

## The mental model — two families
| Family | The image is… | Renderer | You supply |
|---|---|---|---|
| **Color** | `rgb(F(R), F(G), F(B))` per pixel | `render_rgb` | three fields `R,G,B` |
| **Set**   | the region `{ (x,y) \| T(x,y) > 0 }` | `render_set` | one field `T` |

`F` is the byte clamp `floor(255·clamp(x,0,1))` (soft, double-exponential).
Color channels must land in ~[0,1] when using `intensity=F`; for free-form
direct colors return 0..255 and pass `intensity=clip255`.

## The vocabulary (compose, don't re-derive)
`mathart.primitives` — math atoms:
`double_exp(u)=e^(-e^u)`, `soft_step`, `soft_window`, `bump`, `arctan_env`,
`warp`, `clamp01`, and the layering operators `stack_sum` (ADD many objects)
and `stack_product` (MASK/intersect many regions).

`mathart.shapes` — recognizable forms (return signed fields `>0` inside, or
`[0,1]` masks): `ellipse`, `capsule`, `fir`, `bird`, `sun_glow`, `ridge`, `fbm`,
plus combinators `union`, `intersect`, `to_mask`.

`mathart.canvas.Canvas` — pixel→coordinate grid (vectorized). Use
`Canvas.yeganeh(w,h,scale)` for the centered/flipped mapping, or construct
`Canvas(w,h,x0,x_scale,y0,y_scale)` for an exact published mapping.

## Recipe — create a NEW work
1. Copy `mathart/works/_template.py` to `mathart/works/<name>.py`.
2. Pick a family; delete the other half of the template.
   - Color: build `R,G,B` from `shapes`/`primitives`; composite with
     `color*(1-mask) + ink*mask`. Layer many elements with `stack_sum`.
   - Set: build `T` as `union(part1, part2, ...)`; intersect with `*`; stream
     fine detail (hair, feathers) with `stack_sum` of `capsule`s.
3. Register `render` in `mathart/works/__init__.py` under `REGISTRY`.
4. `python -m mathart.cli render <name>` → view → iterate.
5. `python -m mathart.validate_work <name>` as a quick guard before/after
   viewing — it thumbnails the work and FAILs on an all-black or flat/empty
   frame (the two silent failures). Run with no args to validate every work.

## Recipe — reproduce an EXACT published piece
The engine is built for drop-in transcription:
1. Set the canvas to the stated size and mapping (e.g. `x=(m-980)/900`).
2. Transcribe each channel `R/G/B` (or `T`) verbatim into a work module using
   the primitives. Keep `intensity=F`.
3. Render and compare to the source. See `works/wind_turbines_exact.py` for a
   worked example, including how it flags which sub-terms were legible.
Watch for `e^(-e^(...))` (DOUBLE exponential) vs `e^(...)`; misreading this is
the most common transcription error.

## Performance & gotchas
- ALWAYS vectorize: evaluate fields on the whole `(X,Y)` grid; never loop pixels.
- Clip exponent arguments (`np.clip(u,-700,700)`) before `np.exp` to avoid overflow.
- Render small (e.g. 300×200) while iterating; go to full size only when happy.
- `intensity=F` expects channels in ~[0,1]; values >1 are clamped to 0 by F's
  upper soft-step (a frequent "why is it black?" surprise).
- Run `python tests/test_engine.py` after edits; add a render check for new works.
- When generating autonomously, finish with `python -m mathart.validate_work`
  (exit code is non-zero if any work is black/empty) as a batch guard-rail.
