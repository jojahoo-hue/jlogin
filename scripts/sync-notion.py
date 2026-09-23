#!/usr/bin/env python3
"""
Sync Notion pages et bases de données vers les fichiers de contexte Jarvis.

Usage : python3 scripts/sync-notion.py
Dépendances : pip install notion-client python-dotenv

Améliorations par rapport à la version initiale :
- Pagination complète (plus de troncature silencieuse à 100 éléments)
- Lecture récursive des blocs imbriqués (toggles, sous-listes, tableaux)
- Retry avec backoff sur les erreurs de rate limit (429) et transitoires (5xx)
- Routage correct par type, avec détection automatique page / base de données
- Synchro incrémentale non destructive (fusion au lieu d'écrasement) pour les
  sources volumineuses comme les transcriptions
- last_sync suivi par source, avancé uniquement en cas de succès
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    from notion_client import Client
    from dotenv import load_dotenv
except ImportError:
    print("Dépendances manquantes. Lancer : pip install notion-client python-dotenv")
    sys.exit(1)

load_dotenv()

ROOT = Path(__file__).parent.parent
CONFIG_FILE = ROOT / "notion-config.json"
HISTORY_FILE = ROOT / "context" / "HISTORY.md"
BODY_MARKER = "<!-- notion-sync-body -->"

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
if not NOTION_TOKEN:
    print("Erreur : variable NOTION_TOKEN manquante.")
    print("Créer un fichier .env à la racine avec : NOTION_TOKEN=secret_xxxx")
    sys.exit(1)

notion = Client(auth=NOTION_TOKEN)


# --------------------------------------------------------------------------- #
# Utilitaires réseau : retry + pagination
# --------------------------------------------------------------------------- #

def _with_retry(fn, *args, **kwargs):
    """Appelle une fonction de l'API Notion avec retry exponentiel sur rate limit."""
    delay = 1.0
    for attempt in range(5):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            status = getattr(e, "status", None)
            if status is None:
                resp = getattr(e, "response", None)
                status = getattr(resp, "status_code", None)
            code = getattr(e, "code", None)
            transient = status in (429, 500, 502, 503, 504) or code == "rate_limited"
            if not transient or attempt == 4:
                raise
            # Notion renvoie parfois un Retry-After ; sinon backoff exponentiel
            wait = delay
            headers = getattr(getattr(e, "response", None), "headers", None) or {}
            retry_after = headers.get("Retry-After") or headers.get("retry-after")
            if retry_after:
                try:
                    wait = float(retry_after)
                except (TypeError, ValueError):
                    pass
            time.sleep(wait)
            delay *= 2
    raise RuntimeError("Retry épuisé")  # sécurité, ne devrait pas être atteint


def _paginate(list_fn, **kwargs):
    """Itère sur tous les résultats d'un endpoint paginé Notion."""
    cursor = None
    while True:
        call_kwargs = dict(kwargs)
        if cursor:
            call_kwargs["start_cursor"] = cursor
        resp = _with_retry(list_fn, **call_kwargs)
        for item in resp.get("results", []):
            yield item
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")


# --------------------------------------------------------------------------- #
# Extraction de texte : blocs et propriétés
# --------------------------------------------------------------------------- #

def _rich(block: dict, key: str) -> str:
    """Concatène le texte brut d'un tableau rich_text d'un bloc."""
    return "".join(rt.get("plain_text", "") for rt in block.get(key, {}).get("rich_text", []))


def render_blocks(block_id: str, indent: int = 0) -> list:
    """Rend récursivement le contenu d'une page ou d'un bloc en lignes markdown."""
    lines = []
    pad = "  " * indent
    for block in _paginate(notion.blocks.children.list, block_id=block_id):
        t = block.get("type", "")
        text = _rich(block, t)

        if t == "heading_1":
            lines.append(f"{pad}# {text}")
        elif t == "heading_2":
            lines.append(f"{pad}## {text}")
        elif t == "heading_3":
            lines.append(f"{pad}### {text}")
        elif t == "bulleted_list_item":
            lines.append(f"{pad}- {text}")
        elif t == "numbered_list_item":
            lines.append(f"{pad}1. {text}")
        elif t == "to_do":
            checked = block.get("to_do", {}).get("checked", False)
            lines.append(f"{pad}- [{'x' if checked else ' '}] {text}")
        elif t == "toggle":
            lines.append(f"{pad}- {text}")
        elif t == "quote":
            lines.append(f"{pad}> {text}")
        elif t == "callout":
            lines.append(f"{pad}> {text}")
        elif t == "code":
            lang = block.get("code", {}).get("language", "")
            lines.append(f"{pad}```{lang}\n{text}\n{pad}```")
        elif t == "divider":
            lines.append(f"{pad}---")
        elif t == "child_page":
            title = block.get("child_page", {}).get("title", "")
            lines.append(f"{pad}- [page] {title}")
        elif t == "table":
            lines.extend(_render_table(block.get("id", ""), pad))
            continue  # les table_row sont déjà consommées
        elif text.strip():
            lines.append(f"{pad}{text}")

        # Récursion sur les enfants (sauf tableaux et sous-pages, déjà traités)
        if block.get("has_children") and t not in ("table", "child_page"):
            lines.extend(render_blocks(block.get("id", ""), indent + 1))

    return lines


def _render_table(table_id: str, pad: str) -> list:
    """Rend un tableau Notion en tableau markdown."""
    rows = []
    for row in _paginate(notion.blocks.children.list, block_id=table_id):
        if row.get("type") != "table_row":
            continue
        cells = row.get("table_row", {}).get("cells", [])
        texts = ["".join(rt.get("plain_text", "") for rt in cell) for cell in cells]
        rows.append(texts)
    if not rows:
        return []
    out = [f"{pad}| " + " | ".join(rows[0]) + " |",
           f"{pad}| " + " | ".join("---" for _ in rows[0]) + " |"]
    for r in rows[1:]:
        out.append(f"{pad}| " + " | ".join(r) + " |")
    return out


def prop_to_text(prop: dict) -> str:
    """Convertit une propriété de base de données en texte lisible."""
    t = prop.get("type")
    if t == "title":
        return "".join(x.get("plain_text", "") for x in prop.get("title", []))
    if t == "rich_text":
        return "".join(x.get("plain_text", "") for x in prop.get("rich_text", []))
    if t == "select":
        return (prop.get("select") or {}).get("name", "")
    if t == "status":
        return (prop.get("status") or {}).get("name", "")
    if t == "multi_select":
        return ", ".join(o.get("name", "") for o in prop.get("multi_select", []))
    if t == "date":
        d = prop.get("date") or {}
        s = d.get("start", "") or ""
        if d.get("end"):
            s += f" → {d['end']}"
        return s
    if t == "checkbox":
        return "oui" if prop.get("checkbox") else "non"
    if t == "number":
        n = prop.get("number")
        return str(n) if n is not None else ""
    if t == "url":
        return prop.get("url", "") or ""
    if t == "people":
        return ", ".join(p.get("name", "") for p in prop.get("people", []))
    if t == "formula":
        f = prop.get("formula", {})
        return str(f.get(f.get("type"), ""))
    return ""


def page_title(page: dict) -> str:
    """Extrait le titre d'une page/entrée de base."""
    for v in page.get("properties", {}).values():
        if v.get("type") == "title":
            return "".join(x.get("plain_text", "") for x in v.get("title", [])) or "Sans titre"
    return "Sans titre"


# --------------------------------------------------------------------------- #
# Détection page / base de données
# --------------------------------------------------------------------------- #

def detect_kind(obj_id: str) -> str:
    """Détermine si un ID Notion est une base de données ou une page."""
    try:
        _with_retry(notion.databases.retrieve, database_id=obj_id)
        return "database"
    except Exception:
        return "page"


# --------------------------------------------------------------------------- #
# Rendus par mode
# --------------------------------------------------------------------------- #

def query_rows(db_id: str, after: str | None = None) -> list:
    """Renvoie toutes les entrées d'une base, triées, avec filtre incrémental optionnel."""
    kwargs = {"sorts": [{"timestamp": "created_time", "direction": "descending"}]}
    if after:
        kwargs["filter"] = {
            "timestamp": "last_edited_time",
            "last_edited_time": {"after": after},
        }
    return list(_paginate(notion.databases.query, database_id=db_id, **kwargs))


def render_summary(rows: list) -> str:
    """Liste synthétique : titre, date de création, statut/catégorie si présents."""
    if not rows:
        return "[Base de données vide]"
    lines = []
    for page in rows:
        title = page_title(page)
        created = page.get("created_time", "")[:10]
        extras = []
        for prop in page.get("properties", {}).values():
            if prop.get("type") in ("select", "status", "multi_select"):
                val = prop_to_text(prop)
                if val:
                    extras.append(val)
        suffix = f" — {', '.join(extras)}" if extras else ""
        lines.append(f"- **{title}** ({created}){suffix}")
    return "\n".join(lines)


def render_rows_full(rows: list) -> str:
    """Contenu complet de chaque entrée d'une base (titre + blocs de la page)."""
    if not rows:
        return ""
    sections = []
    for page in rows:
        title = page_title(page)
        created = page.get("created_time", "")[:10]
        body = "\n".join(render_blocks(page.get("id", "")))
        sections.append(f"## {title} ({created})\n\n{body}".rstrip())
    return "\n\n---\n\n".join(sections)


# --------------------------------------------------------------------------- #
# Écriture des fichiers de destination
# --------------------------------------------------------------------------- #

def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _rel(p: Path) -> str:
    """Chemin relatif au repo si possible, sinon chemin brut (affichage)."""
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def write_full(destination: Path, label: str, content: str):
    """Écrit (écrase) le fichier de destination avec le contenu complet."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    output = f"# {label}\n\n> Synchronisé depuis Notion le {_timestamp()}\n\n---\n\n{content}\n"
    destination.write_text(output, encoding="utf-8")
    print(f"    Écrit : {_rel(destination)}")


def write_incremental(destination: Path, label: str, new_content: str):
    """Fusionne les nouvelles sections en tête, sans détruire l'existant."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    header = f"# {label}\n\n> Dernière sync incrémentale : {_timestamp()}\n\n{BODY_MARKER}\n"

    old_body = ""
    if destination.exists():
        txt = destination.read_text(encoding="utf-8")
        if BODY_MARKER in txt:
            old_body = txt.split(BODY_MARKER, 1)[1].lstrip("\n")

    if new_content.strip():
        body = new_content.rstrip() + ("\n\n---\n\n" + old_body if old_body else "\n")
    else:
        body = old_body or "[Aucune entrée pour le moment]\n"

    destination.write_text(header + "\n" + body, encoding="utf-8")
    print(f"    Écrit : {_rel(destination)}")


# --------------------------------------------------------------------------- #
# Historique
# --------------------------------------------------------------------------- #

def update_history(synced: list):
    """Ajoute une entrée de sync dans HISTORY.md."""
    today = datetime.now().strftime("%Y-%m-%d")
    entry = f"\n## {today}\n\n### Synchronisation Notion\n"
    for source in synced:
        entry += f"- {source['label']} synchronisé vers `{source['destination']}`\n"

    if HISTORY_FILE.exists():
        existing = HISTORY_FILE.read_text(encoding="utf-8")
        header_end = existing.find("\n## ")
        new_content = existing + entry if header_end == -1 else existing[:header_end] + entry + existing[header_end:]
    else:
        new_content = "# HISTORY.md\n" + entry

    HISTORY_FILE.write_text(new_content, encoding="utf-8")


# --------------------------------------------------------------------------- #
# Traitement d'une source
# --------------------------------------------------------------------------- #

def process_source(source: dict, global_last_sync: str | None):
    """Traite une source selon son type. Lève une exception en cas d'échec."""
    source_type = source.get("type", "")
    obj_id = source.get("id", "")
    destination = ROOT / source["destination"]
    # last_sync par source si disponible, sinon global (rétro-compatible)
    after = source.get("last_synced") or global_last_sync

    if source_type in ("resumes", "chatgpt_archives"):
        # Bases volumineuses : liste synthétique reconstruite intégralement
        rows = query_rows(obj_id)
        write_full(destination, source["label"], render_summary(rows))
        print(f"    {len(rows)} entrée(s)")

    elif source_type == "transcriptions_plaud":
        # Contenu complet, incrémental et non destructif
        rows = query_rows(obj_id, after=after)
        write_incremental(destination, source["label"], render_rows_full(rows))
        print(f"    {len(rows)} nouvelle(s) entrée(s)")

    else:
        # projets et types inconnus : détection auto page / base de données
        kind = detect_kind(obj_id)
        if kind == "database":
            rows = query_rows(obj_id)
            write_full(destination, source["label"], render_rows_full(rows) or "[Base vide]")
            print(f"    base de données, {len(rows)} entrée(s)")
        else:
            content = "\n".join(render_blocks(obj_id))
            write_full(destination, source["label"], content or "[Page vide]")
            print("    page")


def main():
    if not CONFIG_FILE.exists():
        print(f"Fichier de config manquant : {CONFIG_FILE}")
        sys.exit(1)

    config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    sources = config.get("sources", [])
    if not sources:
        print("Aucune source configurée dans notion-config.json")
        sys.exit(0)

    global_last_sync = config.get("last_sync")
    now_iso = datetime.now(timezone.utc).isoformat()

    print(f"Synchronisation de {len(sources)} source(s) Notion...\n")
    synced, failed = [], []

    for source in sources:
        page_id = source.get("id", "")
        if not page_id or "REMPLACER" in page_id:
            print(f"  Ignoré (non configuré) : {source['label']}")
            continue

        print(f"  Lecture : {source['label']}")
        try:
            process_source(source, global_last_sync)
            source["last_synced"] = now_iso  # avancé uniquement en cas de succès
            synced.append(source)
        except Exception as e:
            print(f"    ÉCHEC : {e}")
            failed.append(source["label"])

    if synced:
        update_history(synced)
        if not failed:
            config["last_sync"] = now_iso
        CONFIG_FILE.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")

    print()
    print(f"Sync terminée. {len(synced)} source(s) à jour, {len(failed)} échec(s).")
    if failed:
        print("Sources en échec : " + ", ".join(failed))
        sys.exit(1)


if __name__ == "__main__":
    main()
