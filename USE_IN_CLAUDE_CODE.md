# Use `mathart` as a skill in Claude Code

This bundle is both a working Python package and a Claude Code **skill**
(`SKILL.md` at the project root).

## 1. Drop it into a Claude Code session

```bash
# from wherever you unzip mathart.zip
unzip mathart.zip
cd mathart
```

Make the skill discoverable to Claude Code. Either:

**A. Project skill (recommended)** — keep the folder in your project and point
Claude Code's skills directory at it:
```bash
mkdir -p ~/.claude/skills
ln -s "$(pwd)" ~/.claude/skills/mathart      # or: cp -r . ~/.claude/skills/mathart
```

**B. Just open the folder** in Claude Code and tell it:
> "Read SKILL.md and use it to create math art."

## 2. Install the runtime (numpy + pillow)

```bash
pip install -e . --break-system-packages
python -m mathart.cli list
```

## 3. Drive it

Ask Claude Code things like:
- "Render the forest at 2000×1200 and show me."
- "Add a new work: a flock of birds over the sea, in the color family."
- "Reproduce the Yeganeh horse — transcribe its T(x,y) into a work module."

Claude Code will follow `SKILL.md`: copy `works/_template.py`, compose from
`mathart.primitives` and `mathart.shapes`, register in `works/__init__.py`,
render to `gallery/`, and iterate by viewing the PNG.

## 4. Guard-rail when generating autonomously

```bash
python -m mathart.validate_work          # validate every work
python -m mathart.validate_work horse     # or a subset
python -m mathart.validate_work --out gallery/thumbs   # also dump thumbnails
```

Each work is thumbnailed and checked; it FAILs on an all-black or flat/empty
frame (the two silent failure modes). The exit code is non-zero if any work
fails, so it doubles as a CI / autonomy gate.

## Layout
```
mathart/
  SKILL.md                 <- the skill (read this first)
  USE_IN_CLAUDE_CODE.md    <- this file
  README.md
  pyproject.toml
  mathart/                 <- the engine package
    canvas.py intensity.py primitives.py shapes.py
    renderers/  works/  cli.py
  tests/
  gallery/                 <- output PNGs
```
