#!/usr/bin/env python3
"""
Action 2 : sauvegarde, dédoublonne et renumérote la base Notion Manuscrits.

Constat de départ (vérifié le 2026-09-12) :
  Thot Mfumu TuTi dia Tiya : 107 lignes, 86 titres distincts, 39 numéros distincts
  Nza Nga dia KiTuni       :  58 lignes, 56 titres distincts, 38 numéros distincts
  Nza Ngai dia Nzayi       :  32 lignes, 32 titres distincts, 20 numéros distincts
  Nza Ngai dia Ndosi       :  57 lignes, 57 titres distincts, 48 numéros distincts

Le script procède dans cet ordre, et c'est important :
  1. il exporte TOUS les chapitres en .md sous livres/<livre>/chapitres/
  2. il produit un rapport des doublons et des collisions de numéro
  3. avec --apply seulement, il archive les doublons et renumérote

Un chapitre archivé part à la corbeille Notion, restaurable 30 jours,
et sa copie .md reste dans le dépôt git. Rien n'est perdu.

Usage :
  python3 scripts/manuscrits_dedup.py                 # export + rapport
  python3 scripts/manuscrits_dedup.py --apply         # + archive et renumérote
  python3 scripts/manuscrits_dedup.py --livre "Tablette de Thot"
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from corpus_lib import (
    DB_MANUSCRITS,
    Notion,
    ROOT,
    blocks_to_markdown,
    plain,
    slug,
    write_if_changed,
)

LIVRES_DIR = ROOT / "livres"
RAPPORT = ROOT / "reports" / "manuscrits-doublons.md"


def cle_titre(titre: str) -> str:
    """Titre normalisé pour comparer : sans accents, sans ponctuation, sans numéro."""
    t = unicodedata.normalize("NFD", titre.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = re.sub(r"^chapitre\s*\d+\s*[-–—:.]*\s*", "", t)
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--livre", default="", help="ne traite qu'un livre")
    args = ap.parse_args()

    notion = Notion()
    print(f"Lecture de la base Manuscrits ({DB_MANUSCRITS})…")

    chapitres = []
    for row in notion.query_database(DB_MANUSCRITS):
        p = row.get("properties", {})
        livre = plain(p.get("Livre")) or "Sans livre"
        if args.livre and livre != args.livre:
            continue
        numero_txt = plain(p.get("Numéro"))
        mots_txt = plain(p.get("Mots"))
        chapitres.append({
            "id": row["id"],
            "url": row.get("url", ""),
            "titre": plain(p.get("Titre du Chapitre")) or "Sans titre",
            "livre": livre,
            "numero": int(float(numero_txt)) if numero_txt else None,
            "mots": int(float(mots_txt)) if mots_txt else 0,
            "statut": plain(p.get("Statut")),
            "methode": plain(p.get("Méthode")),
            "date": plain(p.get("Date de rédaction")) or (row.get("created_time") or "")[:10],
            "cree": row.get("created_time", ""),
            "edite": row.get("last_edited_time", ""),
        })

    print(f"  {len(chapitres)} chapitres lus")

    # ---- 1. sauvegarde locale -------------------------------------------
    print("Export des chapitres en markdown…")
    ecrits = 0
    for ch in chapitres:
        corps = blocks_to_markdown(notion.block_children(ch["id"]))
        ch["taille"] = len(corps)
        dossier = LIVRES_DIR / slug(ch["livre"], 40) / "chapitres"
        num = f"{ch['numero']:02d}" if ch["numero"] is not None else "xx"
        chemin = dossier / f"{num}-{slug(ch['titre'])}-{ch['id'][:8]}.md"
        contenu = (
            f"---\n"
            f"notion_id: {ch['id']}\n"
            f"notion_url: {ch['url']}\n"
            f"livre: \"{ch['livre']}\"\n"
            f"numero: {ch['numero'] if ch['numero'] is not None else 'null'}\n"
            f"titre: \"{ch['titre'].replace(chr(34), chr(39))}\"\n"
            f"statut: {ch['statut'] or 'inconnu'}\n"
            f"methode: {ch['methode'] or 'inconnue'}\n"
            f"mots: {ch['mots']}\n"
            f"date: {ch['date']}\n"
            f"---\n\n"
            f"# {ch['titre']}\n\n{corps}\n"
        )
        if write_if_changed(chemin, contenu):
            ecrits += 1
        ch["fichier"] = str(chemin.relative_to(ROOT))
    print(f"  {ecrits} fichiers écrits sous livres/")

    # ---- 2. analyse ------------------------------------------------------
    par_livre = defaultdict(list)
    for ch in chapitres:
        par_livre[ch["livre"]].append(ch)

    doublons: list[dict] = []
    collisions: list[dict] = []
    renumerotations: list[dict] = []

    for livre, items in par_livre.items():
        # doublons de titre
        groupes = defaultdict(list)
        for ch in items:
            groupes[cle_titre(ch["titre"])].append(ch)
        a_archiver = set()
        for cle, grp in groupes.items():
            if len(grp) < 2:
                continue
            # on garde la version la plus fournie, puis la plus récente
            garde = max(grp, key=lambda c: (c["taille"], c["mots"], c["edite"]))
            for ch in grp:
                if ch["id"] != garde["id"]:
                    a_archiver.add(ch["id"])
                    doublons.append({
                        "id": ch["id"],
                        "livre": livre,
                        "titre": ch["titre"],
                        "archive": ch["url"],
                        "conserve": garde["url"],
                        "taille_archive": ch["taille"],
                        "taille_conserve": garde["taille"],
                    })

        restants = [c for c in items if c["id"] not in a_archiver]

        # collisions de numéro
        par_num = defaultdict(list)
        for ch in restants:
            if ch["numero"] is not None:
                par_num[ch["numero"]].append(ch)
        for num, grp in sorted(par_num.items()):
            if len(grp) > 1:
                collisions.append({
                    "livre": livre,
                    "numero": num,
                    "titres": [c["titre"] for c in grp],
                })

        # renumérotation séquentielle : ordre = numéro existant, puis date de création
        restants.sort(key=lambda c: (c["numero"] if c["numero"] is not None else 9999, c["cree"]))
        for i, ch in enumerate(restants, start=1):
            if ch["numero"] != i:
                renumerotations.append({
                    "id": ch["id"],
                    "livre": livre,
                    "titre": ch["titre"],
                    "avant": ch["numero"],
                    "apres": i,
                    "url": ch["url"],
                })

    ecrire_rapport(par_livre, doublons, collisions, renumerotations)

    print()
    print("Analyse")
    for livre, items in sorted(par_livre.items(), key=lambda x: -len(x[1])):
        d = sum(1 for x in doublons if x["livre"] == livre)
        print(f"  {livre:32s} {len(items):4d} lignes, {d:3d} doublons")
    print(f"  doublons de titre      : {len(doublons)}")
    print(f"  collisions de numéro   : {len(collisions)}")
    print(f"  chapitres à renuméroter: {len(renumerotations)}")
    print(f"  rapport détaillé       : {RAPPORT.relative_to(ROOT)}")

    if not args.apply:
        print()
        print("Rapport seul, rien n'a été modifié dans Notion.")
        print("Relis le rapport, puis relance avec --apply.")
        return 0

    print()
    print("Archivage des doublons…")
    for d in doublons:
        notion.archive_page(d["id"])
    print(f"  {len(doublons)} chapitres envoyés à la corbeille Notion")

    print("Renumérotation…")
    for r in renumerotations:
        notion.update_page(r["id"], {"Numéro": {"number": r["apres"]}})
    print(f"  {len(renumerotations)} numéros corrigés")

    print()
    print(f"Terminé. {notion.calls} appels API.")
    return 0


def ecrire_rapport(par_livre, doublons, collisions, renumerotations) -> None:
    lignes = [
        "# Manuscrits : doublons et numérotation",
        "",
        f"Généré le {datetime.now(timezone.utc).strftime('%Y-%m-%d')}.",
        "",
        "## Vue d'ensemble",
        "",
        "| Livre | Lignes | Doublons | À renuméroter |",
        "|---|---:|---:|---:|",
    ]
    for livre, items in sorted(par_livre.items(), key=lambda x: -len(x[1])):
        d = sum(1 for x in doublons if x["livre"] == livre)
        r = sum(1 for x in renumerotations if x["livre"] == livre)
        lignes.append(f"| {livre} | {len(items)} | {d} | {r} |")

    lignes += ["", "## Doublons de titre", ""]
    if doublons:
        lignes += ["| Livre | Titre | Conservé (car.) | Archivé (car.) |", "|---|---|---:|---:|"]
        for d in doublons:
            lignes.append(
                f"| {d['livre']} | {d['titre']} | [{d['taille_conserve']}]({d['conserve']}) "
                f"| [{d['taille_archive']}]({d['archive']}) |"
            )
    else:
        lignes.append("_Aucun._")

    lignes += ["", "## Collisions de numéro", ""]
    if collisions:
        for c in collisions:
            lignes.append(f"- **{c['livre']}** numéro {c['numero']} : " + " / ".join(c["titres"]))
    else:
        lignes.append("_Aucune._")

    lignes += ["", "## Renumérotation proposée", ""]
    if renumerotations:
        lignes += ["| Livre | Avant | Après | Titre |", "|---|---:|---:|---|"]
        for r in renumerotations:
            lignes.append(
                f"| {r['livre']} | {r['avant'] if r['avant'] is not None else '-'} "
                f"| {r['apres']} | [{r['titre']}]({r['url']}) |"
            )
    else:
        lignes.append("_Aucune._")

    RAPPORT.parent.mkdir(parents=True, exist_ok=True)
    RAPPORT.write_text("\n".join(lignes) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
