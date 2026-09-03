#!/usr/bin/env python3
"""
Crée la base Notion qui recevra les notes Apple migrées.

Usage :
    python3 scripts/create-notion-database.py --dry-run
    python3 scripts/create-notion-database.py --parent-page 2d892f894f8c8...

L'ID de page parente se lit dans l'URL Notion de la page qui doit contenir la
base : notion.so/Ma-page-2d892f894f8c81f789f8e1fcfcb851cd -> tout ce qui suit
le dernier tiret. Cette page doit être partagée avec l'intégration Notion.

Le script crée la base avec les propriétés attendues par la migration, puis
inscrit son identifiant dans notion-config.json. Il n'y a rien à recopier
à la main ensuite : `python3 scripts/apple-notes-to-notion.py` est prêt.

Dépendances : pip install notion-client python-dotenv
Jeton       : NOTION_TOKEN dans le fichier .env
"""

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from apple_notes_to_notion import (  # noqa: E402
    CONFIG_FILE,
    DEFAULT_TITLE_PROPERTY,
    build_database_schema,
    update_config_target,
)

DEFAULT_DATABASE_TITLE = "Notes Apple"


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Crée la base Notion cible de la migration Apple Notes.")
    parser.add_argument("--parent-page", help="ID de la page Notion qui contiendra la base")
    parser.add_argument("--title", default=DEFAULT_DATABASE_TITLE, help="Titre de la base à créer")
    parser.add_argument("--config", default=str(CONFIG_FILE), help="Fichier de configuration")
    parser.add_argument("--dry-run", action="store_true", help="Afficher le schéma sans rien créer")
    parser.add_argument("--force", action="store_true", help="Créer même si une cible est déjà configurée")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    config_file = Path(args.config)
    if not config_file.exists():
        print(f"Fichier de config manquant : {config_file}")
        return 1

    config = json.loads(config_file.read_text(encoding="utf-8"))
    apple_notes = config.get("apple_notes", {})
    mapping = apple_notes.get("properties", {})
    title_property = apple_notes.get("title_property", DEFAULT_TITLE_PROPERTY)
    schema = build_database_schema(mapping, title_property)

    print(f"Base à créer : « {args.title} »")
    for name, definition in schema.items():
        print(f"  - {name} : {next(iter(definition))}")

    if args.dry_run:
        print("\nSimulation : rien n'a été créé.")
        print("Relancer avec --parent-page <ID> pour créer la base pour de vrai.")
        return 0

    existing = apple_notes.get("target", {}).get("id", "")
    if existing and "REMPLACER" not in existing and not args.force:
        print(f"\nUne base est déjà configurée : {existing}")
        print("Utiliser --force pour en créer une autre et remplacer la configuration.")
        return 1

    if not args.parent_page:
        print("\nIl manque --parent-page : l'API Notion ne peut créer une base que dans une page existante.")
        print("Copier l'ID depuis l'URL de la page Notion, et partager cette page avec l'intégration.")
        return 1

    try:
        from notion_client import Client
        from dotenv import load_dotenv
    except ImportError:
        print("\nDépendances manquantes. Lancer : pip install notion-client python-dotenv")
        return 1

    load_dotenv()
    token = os.getenv("NOTION_TOKEN")
    if not token:
        print("\nErreur : variable NOTION_TOKEN manquante.")
        print("Créer un fichier .env à la racine avec : NOTION_TOKEN=secret_xxxx")
        return 1

    notion = Client(auth=token)
    try:
        database = notion.databases.create(
            parent={"type": "page_id", "page_id": args.parent_page},
            title=[{"type": "text", "text": {"content": args.title}}],
            properties=schema,
        )
    except Exception as exc:
        print(f"\nEchec de la création : {exc}")
        print("Vérifier que la page parente est bien partagée avec l'intégration Notion.")
        return 1

    database_id = database["id"]
    update_config_target(config_file, database_id)

    print(f"\nBase créée : {database.get('url', database_id)}")
    print(f"Identifiant inscrit dans {config_file.name} : {database_id}")
    print("\nEtape suivante : déposer l'export Apple Notes, puis")
    print("  python3 scripts/apple-notes-to-notion.py --dry-run")
    return 0


if __name__ == "__main__":
    sys.exit(main())
