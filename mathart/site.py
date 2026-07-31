"""Build the gallery site manifest: scan created artefacts → manifest.json.

The companion static site (`index.html` at the repo root) reads `manifest.json`
and lets you browse, filter (by date / type / format), search, favourite and
group the daily math-art creations into collections — no server required, so it
works both locally (open the file) and on GitHub Pages.

Run:  python -m mathart.cli site           # scans ./gallery, writes manifest.json
"""

from __future__ import annotations

import json
import os
import re
import time
from typing import List

# Which folders to index. `input/` (personal photos) is intentionally excluded
# from the published manifest by default — pass extra dirs explicitly if wanted.
DEFAULT_DIRS = ("gallery",)
EXTS = {".png", ".svg", ".json"}

# motif families, for the "type" facet
SACRED = {"wheel", "seal", "flower", "metatron", "mandala",
          "spiral", "enneagram", "sri-yantra"}
SCRIBES = {"harmonograph", "spirograph", "lissajous", "rose",
           "phyllotaxis", "superformula", "streamlines", "attractor"}
WORKS = {"forest", "horse", "turbines", "turbines_exact"}

_DATE_DIR = re.compile(r"(?:^|/)(\d{4}-\d{2}-\d{2})(?:/|$)")

# variant/mode suffixes to strip so sibling variations collapse to one "family"
_SUFFIX = re.compile(
    r"-(silhouette|negative|L\d+|h\d+|kal\d+|mod|morph[\d.]+)$", re.I)


def _family(stem: str) -> str:
    """Collapse a file stem to its motif family (drop mode/variant suffixes)."""
    s = stem
    if s.startswith("demo-"):
        s = s[5:]
    prev = None
    while prev != s:                     # strip repeatedly: horse-h12-silhouette
        prev = s
        s = _SUFFIX.sub("", s)
    return s or stem


def _formula_summary(abspath: str) -> str:
    """One-line Fourier-equation summary for a saved trace formula (best effort)."""
    try:
        with open(abspath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and data.get("type") == "fourier-epicycles":
            from . import trace as tr
            return tr.formula_equation(data, top=3).split("\n")[0]
    except Exception:
        pass
    return ""


def _classify_type(relpath: str, stem: str) -> str:
    low = relpath.lower()
    if "trace" in low or stem.endswith((".json",)) or "-morph" in low \
            or "-kal" in low or stem.startswith("demo-"):
        return "trace"
    tokens = set(re.split(r"[^a-z0-9]+", stem.lower()))
    # multi-word sacred names (sri-yantra) — check membership loosely
    if any(t in SACRED for t in tokens) or "yantra" in low or "sri" in low:
        return "sacré"
    if any(t in SCRIBES for t in tokens):
        return "scribe"
    if "negative" in low or "silhouette" in low or "/stencils/" in low:
        return "pochoir"
    if any(t in WORKS for t in tokens):
        return "render"
    return "autre"


def _date_for(relpath: str, abspath: str) -> str:
    m = _DATE_DIR.search(relpath)
    if m:
        return m.group(1)
    try:
        return time.strftime("%Y-%m-%d", time.localtime(os.path.getmtime(abspath)))
    except OSError:
        return "0000-00-00"


def scan(root: str, dirs=DEFAULT_DIRS) -> List[dict]:
    items = []
    for d in dirs:
        base = os.path.join(root, d)
        if not os.path.isdir(base):
            continue
        for dirpath, _, files in os.walk(base):
            for fn in sorted(files):
                ext = os.path.splitext(fn)[1].lower()
                if ext not in EXTS:
                    continue
                abspath = os.path.join(dirpath, fn)
                relpath = os.path.relpath(abspath, root).replace(os.sep, "/")
                stem = os.path.splitext(fn)[0]
                fmt = ext.lstrip(".")
                try:
                    size = os.path.getsize(abspath)
                except OSError:
                    size = 0
                item = {
                    "id": relpath,
                    "name": stem,
                    "path": relpath,
                    "type": _classify_type(relpath, stem),
                    "family": _family(stem),
                    "format": fmt,
                    "date": _date_for(relpath, abspath),
                    "bytes": size,
                }
                if fmt == "json":
                    summ = _formula_summary(abspath)
                    if summ:
                        item["formula"] = summ
                items.append(item)
    # newest first, then by name
    items.sort(key=lambda it: (it["date"], it["name"]), reverse=True)
    return items


def _latest_report(root: str, max_chars: int = 8000) -> dict:
    """Embed the newest reports/*.md so the site can show it with no fetch."""
    rdir = os.path.join(root, "reports")
    if not os.path.isdir(rdir):
        return {}
    mds = [f for f in os.listdir(rdir) if f.lower().endswith(".md")]
    if not mds:
        return {}
    mds.sort(reverse=True)                    # names are ISO datetimes → newest first
    name = mds[0]
    try:
        with open(os.path.join(rdir, name), "r", encoding="utf-8") as f:
            text = f.read(max_chars + 1)
    except OSError:
        return {}
    truncated = len(text) > max_chars
    return {"name": name, "path": f"reports/{name}",
            "text": text[:max_chars], "truncated": truncated}


def build_manifest(root: str = ".", dirs=DEFAULT_DIRS,
                   out: str = "manifest.json") -> dict:
    items = scan(root, dirs)
    families = {}
    for it in items:
        families[it["family"]] = families.get(it["family"], 0) + 1
    manifest = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "count": len(items),
        "types": sorted({it["type"] for it in items}),
        "formats": sorted({it["format"] for it in items}),
        "dates": sorted({it["date"] for it in items}, reverse=True),
        "families": dict(sorted(families.items(),
                                key=lambda kv: (-kv[1], kv[0]))),
        "report": _latest_report(root),
        "items": items,
    }
    blob = json.dumps(manifest, ensure_ascii=False, indent=1)
    path = os.path.join(root, out)
    with open(path, "w", encoding="utf-8") as f:
        f.write(blob)
    # sibling .js so the page also works from a plain file:// double-click
    # (browsers block fetch() of a local file, but a <script> global loads fine)
    js_path = os.path.splitext(path)[0] + ".js"
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("window.__MANIFEST__ = " + blob + ";\n")
    return {"path": path, "count": len(items)}
