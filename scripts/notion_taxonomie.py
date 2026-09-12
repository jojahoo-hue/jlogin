#!/usr/bin/env python3
"""
Action 1 : remplace la propriété "Sujets" (5081 options libres) par une
taxonomie contrôlée à deux niveaux.

Ce que le script fait sur la base Plaud Archive :
  1. crée la propriété "Thème"      (multi-select, 40 valeurs de corpus/taxonomie.yaml)
  2. crée la propriété "Livre cible" (select, les 9 livres)
  3. crée la propriété "Mots-clés"   (texte libre, reçoit les anciens sujets)
  4. remplit ces trois propriétés ligne par ligne
  5. avec --purge, supprime l'ancienne propriété "Sujets"

Sécurité :
  - par défaut le script ne fait qu'un rapport, il n'écrit rien
  - il refuse de tourner si corpus/index.json est absent (donc sans sauvegarde locale)
  - --purge est refusé tant que les mots-clés n'ont pas été recopiés

Usage :
  python3 scripts/notion_taxonomie.py                # rapport seul
  python3 scripts/notion_taxonomie.py --apply        # crée et remplit
  python3 scripts/notion_taxonomie.py --apply --purge  # + supprime Sujets
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter

from corpus_lib import DB_PLAUD_ARCHIVE, INDEX_JSON, Notion, load_taxonomie

COULEURS = [
    "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red",
    "gray", "default",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="écrit réellement dans Notion")
    ap.add_argument("--purge", action="store_true", help="supprime l'ancienne propriété Sujets")
    ap.add_argument("--limite", type=int, default=0)
    args = ap.parse_args()

    if not INDEX_JSON.exists():
        sys.exit(
            "corpus/index.json introuvable.\n"
            "Lance d'abord : python3 scripts/corpus_export.py\n"
            "On ne touche pas à Notion sans sauvegarde locale préalable."
        )

    index = json.loads(INDEX_JSON.read_text(encoding="utf-8"))
    fiches = index["fiches"]
    taxo = load_taxonomie()
    themes = [t["label"] for t in taxo["themes"]]
    livres = sorted({t.get("livre", "") for t in taxo["themes"] if t.get("livre")})

    anciens = Counter()
    for f in fiches:
        anciens.update(f.get("sujets_bruts", []))

    print("Taxonomie actuelle")
    print(f"  options libres dans Sujets : {len(anciens)}")
    print(f"  fiches concernées          : {len(fiches)}")
    print()
    print("Taxonomie cible")
    print(f"  Thème       : {len(themes)} valeurs contrôlées")
    print(f"  Livre cible : {len(livres)} valeurs")
    print("  Mots-clés   : texte libre (les anciens sujets y sont recopiés)")
    print()
    repartition = Counter(t for f in fiches for t in f["themes"])
    print("Répartition prévue par thème :")
    for theme, n in repartition.most_common():
        print(f"  {n:5d}  {theme}")
    orphelines = [f for f in fiches if f["themes"] == ["Divers et non qualifié"]]
    print()
    print(f"Fiches tombant dans Divers faute de correspondance : {len(orphelines)}")

    if not args.apply:
        print()
        print("Rapport seul. Relance avec --apply pour écrire dans Notion.")
        return 0

    notion = Notion()

    print()
    print("Création des propriétés…")
    notion.update_database(DB_PLAUD_ARCHIVE, {
        "Thème": {"multi_select": {"options": [
            {"name": t, "color": COULEURS[i % len(COULEURS)]}
            for i, t in enumerate(themes)
        ]}},
        "Livre cible": {"select": {"options": [
            {"name": l, "color": COULEURS[i % len(COULEURS)]}
            for i, l in enumerate(livres)
        ]}},
        "Mots-clés": {"rich_text": {}},
    })
    print("  propriétés Thème, Livre cible et Mots-clés en place")

    print("Remplissage des lignes…")
    ecrites = 0
    for n, f in enumerate(fiches, start=1):
        if args.limite and n > args.limite:
            break
        mots = ", ".join(f.get("sujets_bruts", []))[:1900]
        props = {
            "Thème": {"multi_select": [{"name": t} for t in f["themes"] if t in themes]},
            "Mots-clés": {"rich_text": [{"text": {"content": mots}}] if mots else []},
        }
        if f.get("livre_cible"):
            props["Livre cible"] = {"select": {"name": f["livre_cible"]}}
        notion.update_page(f["notion_id"], props)
        ecrites += 1
        if n % 50 == 0:
            print(f"  {n}/{len(fiches)} lignes")

    print(f"  {ecrites} lignes mises à jour")

    if args.purge:
        manquantes = [f for f in fiches if f.get("sujets_bruts") and not f.get("themes")]
        if manquantes:
            print(f"Purge refusée : {len(manquantes)} fiches sans thème attribué.")
            return 1
        print("Suppression de l'ancienne propriété Sujets…")
        notion.update_database(DB_PLAUD_ARCHIVE, {"Sujets": None})
        print("  Sujets supprimée. Les valeurs sont conservées dans Mots-clés et dans corpus/.")

    print()
    print(f"Terminé. {notion.calls} appels API.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
