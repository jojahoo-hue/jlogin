"""Nano Banana (Gemini 2.5 Flash Image) bridge — text prompt -> raster -> mask.

This is the *organic / illustrative* counterpart to the exact parametric and
matplotlib motifs: ask an image model for a subject ("a crane in flight, bold
ink silhouette"), then reduce the returned raster to a cuttable mask with
`stencil.posterize_masks` / `stencil.edge_mask` and vectorise as usual.

DORMANT BY DESIGN. No network call happens unless you both:
  1. set GEMINI_API_KEY (or GOOGLE_API_KEY) in the environment, and
  2. have the `google-genai` package installed.
Otherwise `generate_image` raises a clear, actionable RuntimeError. The API key
is read ONLY from the environment — never hard-code it.

Prompting tip for clean pochoirs: ask for "high-contrast black silhouette on a
plain white background, no gradients, no texture" so posterise/edge reduction
yields a single crisp cut layer.
"""

from __future__ import annotations

import os

_MODEL = "gemini-2.5-flash-image"
_STENCIL_STYLE = (
    "high-contrast solid black silhouette on a plain pure-white background, "
    "no gradient, no shading, no texture, centered, clean bold outline"
)


def available() -> bool:
    """True iff a key is present AND the SDK is importable (no call made)."""
    if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")):
        return False
    try:
        import google.genai  # noqa: F401
        return True
    except Exception:
        return False


def _api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError(
            "Nano Banana is dormant: set GEMINI_API_KEY (or GOOGLE_API_KEY) in "
            "your environment. The key is read from the env only — never put it "
            "in code or commit it."
        )
    return key


def generate_image(prompt: str, *, stencil_style: bool = True):
    """Return a PIL image for `prompt` via Gemini 2.5 Flash Image.

    Raises RuntimeError if the SDK is missing or no key is set, so the rest of
    the package keeps working offline.
    """
    key = _api_key()
    try:
        from google import genai
    except Exception as exc:                    # pragma: no cover
        raise RuntimeError(
            "The `google-genai` package is not installed. Install it with "
            "`pip install google-genai` to enable Nano Banana."
        ) from exc

    from io import BytesIO
    from PIL import Image

    full = f"{prompt}. {_STENCIL_STYLE}" if stencil_style else prompt
    client = genai.Client(api_key=key)
    resp = client.models.generate_content(model=_MODEL, contents=full)
    for part in resp.candidates[0].content.parts:
        data = getattr(getattr(part, "inline_data", None), "data", None)
        if data:
            return Image.open(BytesIO(data)).convert("RGB")
    raise RuntimeError("Gemini returned no image part for this prompt.")


def mask_from_prompt(prompt: str, *, reduce: str = "posterize",
                     levels: int = 2, edge_threshold: float = 0.18,
                     thickness: int = 2):
    """Prompt -> image -> single cuttable mask (via stencil reductions)."""
    from . import stencil as st
    img = generate_image(prompt)
    if reduce == "edges":
        return st.edge_mask(img, threshold=edge_threshold, thickness=thickness)
    masks = st.posterize_masks(img, levels=levels)
    return masks[0] if masks else st.mask_from_image(img)
