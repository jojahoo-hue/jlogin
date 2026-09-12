#!/usr/bin/env python3
"""
Action 3 : construit la couche corpus locale depuis la base Notion Plaud Archive.

Produit, pour chaque enregistrement :
  corpus/fiches/AAAA-MM-JJ_<dossier>_<titre>.md
avec un en-tête YAML exploitable par grep, puis résumé, actions, thèmes,
et la transcription intégrale récupérée depuis le corps de la page Notion.

Produit aussi :
  corpus/index.json   inventaire machine, sert de base aux autres scripts
  corpus/INDEX.md     inventaire lisible, groupé par thème

Usage :
  python3 scripts/corpus_export.py                 # incrémental
  python3 scripts/corpus_export.py --full          # réécrit tout
  python3 scripts/corpus_export.py --sans-transcription   # métadonnées seules, rapide
  python3 scripts/corpus_export.py --limite 50     # test sur 50 fiches

Prérequis : .env avec NOTION_TOKEN, et pip3 install pyyaml
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

from corpus_lib import (
    CORPUS,
    DB_PLAUD_ARCHIVE,
    FICHES,
    INDEX_JSON,
    Notion,
    blocks_to_markdown,
    build_matcher,
    fiche_path,
    infer_themes,
    load_taxonomie,
    multi_list,
    plain,
    theme_to_livre,
    write_if_changed,
)

EN_TETE = """---
plaud_id: {plaud_id}
notion_url: {notion_url}
titre: {titre_yaml}
date: {date}
duree_min: {duree}
dossier: {dossier}
statut_plaud: {statut}
themes: [{themes}]
livre_cible: {livre}
mots_cles: {mots_cles}
transcription: {a_transcription}
derniere_maj: {maj}
---

# {titre}

## Résumé

{resume}

## Actions

{actions}

## Sujets bruts (Plaud)

{sujets}
"""


def echappe(text: str) -> str:
    return '"' + text.replace('"', "'").replace("\n", " ").strip() + '"'


def extrait_transcription(markdown: str) -> tuple[str, str, str]:
    """Sépare le corps de page Notion en (résumé, actions, transcription)."""
    resume, actions, transcription = "", "", ""
    courant = None
    tampon: dict[str, list[str]] = defaultdict(list)
    for ligne in markdown.splitlines():
        bas = ligne.strip().lower()
        if bas.startswith("## "):
            if "résumé" in bas or "resume" in bas:
                courant = "resume"
                continue
            if "action" in bas:
                courant = "actions"
                continue
            if "transcription" in bas:
                courant = "transcription"
                continue
            if "sujet" in bas:
                courant = "sujets"
                continue
            courant = None
            continue
        if courant:
            tampon[courant].append(ligne)
    resume = "\n".join(tampon["resume"]).strip()
    actions = "\n".join(tampon["actions"]).strip()
    transcription = "\n".join(tampon["transcription"]).strip()
    return resume, actions, transcription


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true", help="réécrit toutes les fiches")
    ap.add_argument("--sans-transcription", action="store_true",
                    help="n'extrait pas le corps des pages (beaucoup plus rapide)")
    ap.add_argument("--limite", type=int, default=0, help="ne traite que N lignes")
    args = ap.parse_args()

    taxo = load_taxonomie()
    matcher = build_matcher(taxo)
    livres = theme_to_livre(taxo)

    ancien = {}
    if INDEX_JSON.exists() and not args.full:
        ancien = {f["plaud_id"]: f for f in json.loads(INDEX_JSON.read_text())["fiches"]}

    notion = Notion()
    FICHES.mkdir(parents=True, exist_ok=True)

    fiches, ecrites, sautees = [], 0, 0
    print(f"Lecture de la base Plaud Archive ({DB_PLAUD_ARCHIVE})…")

    for n, row in enumerate(notion.query_database(DB_PLAUD_ARCHIVE), start=1):
        if args.limite and n > args.limite:
            break
        props = row.get("properties", {})
        plaud_id = plain(props.get("Plaud_ID"))
        titre = plain(props.get("Titre")) or "Sans titre"
        dossier = plain(props.get("Dossier")) or "Non classé (sans titre)"
        date = plain(props.get("Date")) or (row.get("created_time") or "")[:10]
        duree = plain(props.get("Durée")).replace(" min", "").strip()
        statut = plain(props.get("Statut"))
        resume_prop = plain(props.get("Résumé"))
        actions_prop = plain(props.get("Actions"))
        sujets = multi_list(props.get("Sujets"))
        edite = row.get("last_edited_time", "")
        url = row.get("url", "")

        cle = plaud_id or row["id"]
        precedent = ancien.get(cle)
        if precedent and precedent.get("notion_edite") == edite and not args.full:
            fiches.append(precedent)
            sautees += 1
            continue

        resume, actions, transcription = resume_prop, actions_prop, ""
        if not args.sans_transcription:
            markdown = blocks_to_markdown(notion.block_children(row["id"]))
            r2, a2, transcription = extrait_transcription(markdown)
            resume = r2 or resume
            actions = a2 or actions

        themes = infer_themes(matcher, titre, " ".join(sujets), resume)
        if not themes:
            themes = ["Divers et non qualifié"]
        livre = next((livres.get(t, "") for t in themes if livres.get(t)), "")

        chemin = fiche_path(date, dossier, titre)
        corps = EN_TETE.format(
            plaud_id=plaud_id or "inconnu",
            notion_url=url,
            titre_yaml=echappe(titre),
            date=date or "inconnue",
            duree=duree or "0",
            dossier=echappe(dossier),
            statut=statut or "inconnu",
            themes=", ".join(echappe(t) for t in themes),
            livre=echappe(livre) if livre else '""',
            mots_cles=echappe(", ".join(sujets[:25])),
            a_transcription="oui" if transcription else "non",
            maj=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            titre=titre,
            resume=resume or "_Aucun résumé disponible._",
            actions=actions or "_Aucune action identifiée._",
            sujets=", ".join(sujets) or "_aucun_",
        )
        if transcription:
            corps += f"\n## Transcription intégrale\n\n{transcription}\n"

        if write_if_changed(chemin, corps):
            ecrites += 1

        fiches.append({
            "plaud_id": plaud_id,
            "notion_id": row["id"],
            "notion_url": url,
            "notion_edite": edite,
            "titre": titre,
            "date": date,
            "duree_min": float(duree) if duree.replace(".", "", 1).isdigit() else 0.0,
            "dossier": dossier,
            "statut": statut,
            "themes": themes,
            "livre_cible": livre,
            "sujets_bruts": sujets,
            "fichier": str(chemin.relative_to(CORPUS.parent)),
            "taille_transcription": len(transcription),
        })

        if n % 50 == 0:
            print(f"  {n} lignes traitées ({ecrites} écrites, {sautees} inchangées)")

    index = {
        "genere_le": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": f"https://app.notion.com/p/{DB_PLAUD_ARCHIVE}",
        "total": len(fiches),
        "heures": round(sum(f["duree_min"] for f in fiches) / 60, 1),
        "fiches": fiches,
    }
    INDEX_JSON.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")

    ecrire_index_md(index)

    print()
    print(f"Terminé. {len(fiches)} fiches, {index['heures']} h d'audio.")
    print(f"  {ecrites} fichiers écrits, {sautees} inchangés, {notion.calls} appels API.")
    print(f"  Index : {INDEX_JSON}")
    return 0


def ecrire_index_md(index: dict) -> None:
    par_theme = defaultdict(list)
    par_livre = defaultdict(list)
    for f in index["fiches"]:
        for t in f["themes"]:
            par_theme[t].append(f)
        if f["livre_cible"]:
            par_livre[f["livre_cible"]].append(f)

    lignes = [
        "# Index du corpus",
        "",
        f"Généré le {index['genere_le'][:10]} depuis Notion Plaud Archive.",
        f"**{index['total']} fiches**, **{index['heures']} heures** d'audio.",
        "",
        "## Par livre cible",
        "",
        "| Livre | Fiches | Heures |",
        "|---|---:|---:|",
    ]
    for livre, items in sorted(par_livre.items(), key=lambda x: -len(x[1])):
        heures = round(sum(i["duree_min"] for i in items) / 60, 1)
        lignes.append(f"| {livre} | {len(items)} | {heures} |")

    lignes += ["", "## Par thème", "", "| Thème | Fiches | Heures |", "|---|---:|---:|"]
    for theme, items in sorted(par_theme.items(), key=lambda x: -len(x[1])):
        heures = round(sum(i["duree_min"] for i in items) / 60, 1)
        lignes.append(f"| {theme} | {len(items)} | {heures} |")

    dossiers = Counter(f["dossier"] for f in index["fiches"])
    lignes += ["", "## Par dossier", "", "| Dossier | Fiches |", "|---|---:|"]
    for dossier, n in dossiers.most_common():
        lignes.append(f"| {dossier} | {n} |")

    lignes += [
        "",
        "## Comment chercher",
        "",
        "```bash",
        "# toutes les fiches d'un thème",
        "grep -l 'Sceaux et cartouches' corpus/fiches/*.md",
        "",
        "# un terme dans les transcriptions, avec le nom du fichier",
        "grep -rin 'kalunga' corpus/fiches/ | head -40",
        "",
        "# les fiches d'un livre",
        "grep -l 'livre_cible: \"Nza Nga dia KiTuni\"' corpus/fiches/*.md",
        "```",
        "",
    ]
    (CORPUS / "INDEX.md").write_text("\n".join(lignes), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
