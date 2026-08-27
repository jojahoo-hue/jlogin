#!/usr/bin/env python3
"""
Génère la section "Artefacts" du rapport de routine avec liens vers le site web.
Usage: python scripts/routine_report.py <date> <out_dir>
  date    : YYYY-MM-DD
  out_dir : chemin vers gallery/routine/<date>/
"""

import json
import os
import sys
from pathlib import Path

SITE_URL = "https://jojahoo-hue.github.io/jlogin"
GALLERY_VIEW = f"{SITE_URL}/#"   # hash anchor pour filtrer par date dans le gallery

def links_section(date: str, out_dir: str) -> str:
    out = Path(out_dir)
    if not out.is_dir():
        return f"_Répertoire introuvable : {out_dir}_\n"

    files = sorted(out.iterdir())
    artefacts = [f for f in files if f.suffix in (".svg", ".png")]
    formulae  = [f for f in files if f.suffix == ".json"]

    lines = []
    lines.append(f"## Créations du {date} — Accès au site")
    lines.append("")
    lines.append(f"Galerie complète : [{SITE_URL}]({SITE_URL})")
    lines.append("")

    if artefacts:
        lines.append("| Fichier | Lien direct |")
        lines.append("|---------|-------------|")
        for f in artefacts:
            rel = f"gallery/routine/{date}/{f.name}"
            url = f"{SITE_URL}/{rel}"
            lines.append(f"| `{f.name}` | [voir]({url}) |")
    else:
        lines.append("_Aucun artefact SVG/PNG trouvé._")

    if formulae:
        lines.append("")
        lines.append("**Formules JSON sauvegardées :**")
        for f in formulae:
            rel = f"gallery/routine/{date}/{f.name}"
            url = f"{SITE_URL}/{rel}"
            lines.append(f"- [`{f.name}`]({url})")

    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    date, out_dir = sys.argv[1], sys.argv[2]
    print(links_section(date, out_dir))
