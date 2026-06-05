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
  Also covers sacred-geometry / numerology visuals: turning a word's numeric
  values (V.N, V.S, C.S) into a base-12 wheel of glyphs or a seamless meditative
  p5.js loop. Trigger on "roue base 12", "géométrie sacrée", "sacred wheel",
  "seamless meditation loop", "sceau", "glyph wheel from a number".
  Can also export any motif as a Cricut-ready SVG stencil — silhouette or true
  negative stencil with auto bridges — for cutting paint stencils ("pochoir").
  Trigger on "Cricut", "pochoir", "stencil", "SVG to cut", "vectorise to SVG".
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

## Family 3 — sacred geometry & numerology visuals (p5.js, animated)

A separate visual track: turn a **number** (often the numerology of a word) into a
**base-12 wheel** or a **seamless meditative loop**. Unlike the Python families
above, these are animated and live in `assets/` as p5.js sketches you paste into
[editor.p5js.org](https://editor.p5js.org). The Python engine renders still
images; use this track when the user wants motion, breathing rhythm, or a ritual
seal driven by a number.

### From a number to a wheel
A word can be reduced to numbers (e.g. `V.N` = sum of letter values, `V.S =
A(A+1)/2`, `C.S` = digital root). Those numbers drive the geometry:
- **12 glyphs** in a ring (base 12 = Dikenga's 4 directions × 3 times); each glyph
  is a small segment/angle (`segment`, `angle L`, `chevron`, `hook`).
- **C.S drives the inner rhythm.** If `C.S = 3`, each breath lights **4 glyphs**
  (quadripole: 0–3, 4–7, 8–11) so 3 breaths sweep all 12. If `C.S = 9`, nine
  internal phases modulate the central seal.
- A **central seal** is a 3-turn rose curve, `r(a) = base·(1 + a_struct·sin(4a+φ)
  + a_cycle·sin(12a−φ) + 0.08a)`, with a faint 4-line quadrature for the 4 planes.

### Seamless timing (so the loop never jumps)
- **75 BPM** → 12 beats per loop; beat phase = `2π·12·u`.
- Loop = **9.6 s** (12 × 0.8 s) at **30 fps = 288 frames**, with `u = frame/288`.
- Every oscillator uses integer multiples of `2π·u`, so frame 0 and frame 288 match.

### Templates (in `assets/`)
- `assets/roue_base12_glyphes.js` — 12-glyph wheel + central seal + breathing
  quadripole (`CS = 3`). Edit `CS`, `GLYPH_TYPES`, `GLYPH_TWIST` for the real word.
- `assets/sceau_cs9_loop.js` — central seal alone + 9 internal phases (`CS = 9`,
  calibrated for the worked example "LOGIN").

### Export to MP4
Uncomment the `saveCanvas(...)` + `noLoop()` lines (288 PNGs), then:
```bash
ffmpeg -framerate 30 -i frame_%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 out.mp4
```

> The numerology *calculation* itself (letter→number table, V.N/Z.M/V.S/Àn/C.S)
> belongs to the writing skill `redaction-initiatique`; this skill consumes the
> resulting numbers and renders them.

## Cricut stencil export (SVG, to cut a paint stencil)

Turn any motif into a **vector SVG** Cricut Design Space can cut. Everything goes
through a boolean **mask** → a shared vectoriser (marching squares + Douglas–
Peucker), so the path stays light. Units are **neutral** (`viewBox` only); set the
real size on import. Output is one `<path fill-rule="evenodd">` = one cut layer.

Two modes:
- **silhouette** — the motif's own outline (counters handled by evenodd). Cut the
  shape itself (mask, magnet, applique).
- **negative** — a full frame minus the motif, with **auto bridges**: islands
  (the inside of an "O", a sun disk, gaps between a horse's legs) are tied back to
  the frame so the stencil stays in one piece. This is the real *pochoir* you
  paint through.

### From a registered work
```bash
python -m mathart.cli stencil horse --mode negative --out gallery/stencils
python -m mathart.cli stencil horse --mode silhouette --threshold 128 --invert
```
The work is rendered, then thresholded (`--threshold`, `--invert`) to a mask.

### From parametric sacred geometry (clean vectors)
```bash
python -m mathart.cli sacred wheel --cs 3 --mode silhouette --out gallery/stencils
python -m mathart.cli sacred seal  --mode negative
python -m mathart.cli sacred flower    --mode silhouette  # Flower of Life
python -m mathart.cli sacred metatron  --mode silhouette  # Metatron's Cube
python -m mathart.cli sacred mandala   --petals 8 --rings 4   # N-fold mandala
python -m mathart.cli sacred spiral    --mode silhouette  # golden spiral
python -m mathart.cli sacred enneagram --mode silhouette  # 9-point enneagram
python -m mathart.cli sacred sri-yantra --mode silhouette # Sri Yantra
```
`mathart.sacred` draws each design as thick strokes → mask → same pipeline.
Generators (`mathart.sacred.GENERATORS`): `wheel` (base-12 glyph wheel), `seal`
(rose seal), `flower` (19-circle Flower of Life), `metatron` (Fruit of Life +
joined centres), `mandala` (concentric rings + rose petals + spokes; tune
`--petals`/`--rings`), `spiral` (logarithmic golden spiral φ + nested
rectangles), `enneagram` (circle + 3-6-9 triangle + 1-4-2-8-5-7 web),
`sri-yantra` (9 interlocking triangles + lotus petals + bhupura gates). Drive
`--cs` from the word's Code Secret; `--line-width` sets the paintable band
thickness.

### Knobs & gotchas
- `--max-side` (default 360) = vectorise resolution; higher = smoother + heavier
  path. 300–500 is the Cricut sweet spot.
- `--frame-margin` / `--bridge-width` tune the negative stencil's frame and ties.
  If a stencil falls apart, increase `--bridge-width`; if bridges look clumsy,
  lower it. The motif is auto-padded so it never fuses with the frame.
- **Stroke width matters for paint**: very thin lines won't survive as a stencil —
  keep bands ≥ a few mm once sized. Prefer the `sacred` generators (filled bands)
  over hairline strokes for cuttable geometry.
- Always open the SVG (or its preview) before cutting; confirm the negative
  stencil is a single connected piece (`mathart.stencil._add_bridges` guarantees
  one body, but a too-thin bridge can pinch off after simplification).
- API: `from mathart import stencil; stencil.silhouette_svg(mask)` /
  `stencil.negative_svg(mask, frame_margin=..., bridge_width=...)`;
  `stencil.mask_from_image(img, threshold, invert)` to mask any rendered work.

## Performance & gotchas
- ALWAYS vectorize: evaluate fields on the whole `(X,Y)` grid; never loop pixels.
- Clip exponent arguments (`np.clip(u,-700,700)`) before `np.exp` to avoid overflow.
- Render small (e.g. 300×200) while iterating; go to full size only when happy.
- `intensity=F` expects channels in ~[0,1]; values >1 are clamped to 0 by F's
  upper soft-step (a frequent "why is it black?" surprise).
- Run `python tests/test_engine.py` after edits; add a render check for new works.
- When generating autonomously, finish with `python -m mathart.validate_work`
  (exit code is non-zero if any work is black/empty) as a batch guard-rail.
