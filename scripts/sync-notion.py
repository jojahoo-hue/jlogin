#!/usr/bin/env python3
"""
Sync Notion pages to Jarvis context files.
Usage: python3 scripts/sync-notion.py
Requires: pip install notion-client python-dotenv
"""

import json
import os
import sys
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

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
if not NOTION_TOKEN:
    print("Erreur : variable NOTION_TOKEN manquante.")
    print("Créer un fichier .env à la racine avec : NOTION_TOKEN=secret_xxxx")
    sys.exit(1)

notion = Client(auth=NOTION_TOKEN)


def get_page_content(page_id: str) -> str:
    """Récupère le contenu texte d'une page Notion."""
    try:
        blocks = notion.blocks.children.list(block_id=page_id)
        lines = []
        for block in blocks.get("results", []):
            block_type = block.get("type")
            if block_type in ("paragraph", "heading_1", "heading_2", "heading_3",
                              "bulleted_list_item", "numbered_list_item", "quote", "callout"):
                rich_texts = block.get(block_type, {}).get("rich_text", [])
                text = "".join(rt.get("plain_text", "") for rt in rich_texts)
                if text.strip():
                    if block_type == "heading_1":
                        lines.append(f"# {text}")
                    elif block_type == "heading_2":
                        lines.append(f"## {text}")
                    elif block_type == "heading_3":
                        lines.append(f"### {text}")
                    elif block_type in ("bulleted_list_item",):
                        lines.append(f"- {text}")
                    elif block_type in ("numbered_list_item",):
                        lines.append(f"1. {text}")
                    else:
                        lines.append(text)
        return "\n".join(lines)
    except Exception as e:
        return f"[Erreur lecture page {page_id}: {e}]"


def get_database_content(db_id: str) -> str:
    """Récupère les entrées d'une base de données Notion."""
    try:
        results = notion.databases.query(database_id=db_id)
        lines = []
        for page in results.get("results", []):
            props = page.get("properties", {})
            title_prop = next(
                (v for v in props.values() if v.get("type") == "title"),
                None
            )
            if title_prop:
                title_texts = title_prop.get("title", [])
                title = "".join(t.get("plain_text", "") for t in title_texts)
                last_edited = page.get("last_edited_time", "")[:10]
                lines.append(f"- **{title}** ({last_edited})")
        return "\n".join(lines) if lines else "[Base de données vide]"
    except Exception as e:
        return f"[Erreur lecture base {db_id}: {e}]"


def write_destination(destination: Path, label: str, content: str):
    """Écrit le contenu dans le fichier de destination."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    output = f"# {label}\n\n> Synchronisé depuis Notion le {now}\n\n---\n\n{content}\n"
    destination.write_text(output, encoding="utf-8")
    print(f"  Écrit : {destination.relative_to(ROOT)}")


def update_history(synced_sources: list):
    """Ajoute une entrée de sync dans HISTORY.md."""
    today = datetime.now().strftime("%Y-%m-%d")
    entry = f"\n## {today}\n\n### Synchronisation Notion\n"
    for source in synced_sources:
        entry += f"- {source['label']} synchronisé vers `{source['destination']}`\n"

    if HISTORY_FILE.exists():
        existing = HISTORY_FILE.read_text(encoding="utf-8")
        header_end = existing.find("\n## ")
        if header_end == -1:
            new_content = existing + entry
        else:
            new_content = existing[:header_end] + entry + existing[header_end:]
    else:
        new_content = "# HISTORY.md\n" + entry

    HISTORY_FILE.write_text(new_content, encoding="utf-8")


def main():
    if not CONFIG_FILE.exists():
        print(f"Fichier de config manquant : {CONFIG_FILE}")
        sys.exit(1)

    config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    sources = config.get("sources", [])

    if not sources:
        print("Aucune source configurée dans notion-config.json")
        sys.exit(0)

    print(f"Synchronisation de {len(sources)} source(s) Notion...\n")
    synced = []

    for source in sources:
        page_id = source.get("id", "")
        if "REMPLACER" in page_id:
            print(f"  Ignoré (non configuré) : {source['label']}")
            continue

        print(f"  Lecture : {source['label']}")
        source_type = source.get("type", "")

        if source_type in ("resumes",):
            content = get_database_content(page_id)
        else:
            content = get_page_content(page_id)

        destination = ROOT / source["destination"]
        write_destination(destination, source["label"], content)
        synced.append(source)

    if synced:
        update_history(synced)
        config["last_sync"] = datetime.now(timezone.utc).isoformat()
        CONFIG_FILE.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nSync terminée. {len(synced)} source(s) mises à jour.")
    else:
        print("\nAucune source active. Vérifier les IDs dans notion-config.json")


if __name__ == "__main__":
    main()
