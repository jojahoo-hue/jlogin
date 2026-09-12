#!/usr/bin/env python3
"""
Action 4, partie analyse : compare l'inventaire Plaud et la base Notion,
et produit la liste des enregistrements manquants.

L'inventaire Plaud ne peut être produit que par Claude Code, qui seul dispose
du MCP Plaud. La commande /corpus s'en charge et écrit corpus/plaud-listing.json.
Ce script fait la comparaison et le rapport.

Usage :
  python3 scripts/plaud_gap.py
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timezone

from corpus_lib import CORPUS, INDEX_JSON, ROOT

LISTING = CORPUS / "plaud-listing.json"
MANQUANTS = CORPUS / "plaud-manquants.json"
RAPPORT = ROOT / "reports" / "plaud-ecart.md"


def main() -> int:
    if not INDEX_JSON.exists():
        sys.exit("corpus/index.json absent. Lance d'abord : python3 scripts/corpus_export.py")
    if not LISTING.exists():
        sys.exit(
            "corpus/plaud-listing.json absent.\n"
            "Dans Claude Code, lance : /corpus listing\n"
            "(seul Claude a accès au MCP Plaud)"
        )

    index = json.loads(INDEX_JSON.read_text(encoding="utf-8"))
    listing = json.loads(LISTING.read_text(encoding="utf-8"))

    dans_notion = {f["plaud_id"] for f in index["fiches"] if f.get("plaud_id")}
    plaud = {r["id"]: r for r in listing["enregistrements"]}

    manquants = [r for pid, r in plaud.items() if pid not in dans_notion]
    orphelins = [f for f in index["fiches"] if f.get("plaud_id") and f["plaud_id"] not in plaud]

    manquants.sort(key=lambda r: r.get("created_at", ""), reverse=True)

    MANQUANTS.write_text(json.dumps({
        "genere_le": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total": len(manquants),
        "enregistrements": manquants,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    annees = Counter((r.get("created_at") or "????")[:4] for r in manquants)
    heures = round(sum(r.get("duration", 0) for r in manquants) / 3_600_000, 1)

    lignes = [
        "# Écart entre Plaud et Notion",
        "",
        f"Généré le {datetime.now(timezone.utc).strftime('%Y-%m-%d')}.",
        "",
        f"- Enregistrements sur Plaud : **{len(plaud)}**",
        f"- Fiches dans Notion        : **{len(dans_notion)}**",
        f"- Manquants dans Notion     : **{len(manquants)}** ({heures} h)",
        f"- Présents dans Notion mais absents de Plaud : **{len(orphelins)}**",
        "",
        "## Manquants par année",
        "",
        "| Année | Nombre |",
        "|---|---:|",
    ]
    for annee, n in sorted(annees.items(), reverse=True):
        lignes.append(f"| {annee} | {n} |")

    lignes += ["", "## Liste des manquants", "", "| Date | Durée | Titre |", "|---|---:|---|"]
    for r in manquants:
        duree = round(r.get("duration", 0) / 60000)
        lignes.append(f"| {(r.get('created_at') or '')[:10]} | {duree} min | {r.get('name', '')} |")

    RAPPORT.parent.mkdir(parents=True, exist_ok=True)
    RAPPORT.write_text("\n".join(lignes) + "\n", encoding="utf-8")

    print(f"Plaud   : {len(plaud)} enregistrements")
    print(f"Notion  : {len(dans_notion)} fiches")
    print(f"Manquants : {len(manquants)} ({heures} h)")
    print(f"Orphelins : {len(orphelins)}")
    print(f"Rapport : {RAPPORT.relative_to(ROOT)}")
    print(f"Liste machine : {MANQUANTS.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
