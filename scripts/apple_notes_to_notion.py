#!/usr/bin/env python3
"""
Migre un export Apple Notes (Markdown / texte) vers Notion.

Usage :
    python3 scripts/apple-notes-to-notion.py --dry-run
    python3 scripts/apple-notes-to-notion.py
    python3 scripts/apple-notes-to-notion.py --source chemin/vers/export --limit 5

Configuration : bloc "apple_notes" dans notion-config.json
Dépendances    : pip install notion-client python-dotenv
Jeton          : NOTION_TOKEN dans le fichier .env

Le script est idempotent : il garde la trace de chaque note déjà migrée dans un
fichier d'état local (empreinte du contenu + identifiant de page Notion). Une
note inchangée est ignorée, une note modifiée voit son contenu remplacé dans
Notion, aucune note n'est dupliquée.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONFIG_FILE = ROOT / "notion-config.json"
HISTORY_FILE = ROOT / "context" / "HISTORY.md"
STATE_FILE = ROOT / "apple-notes-sync-state.json"

DEFAULT_SOURCE = "context/import/apple-notes"
NOTE_EXTENSIONS = (".md", ".markdown", ".txt")
SKIPPED_FILENAMES = {"readme.md", "readme.txt", "index.md"}

# Limites de l'API Notion
MAX_TEXT_LENGTH = 2000       # caractères par objet rich_text
MAX_RICH_TEXT_ITEMS = 100    # objets rich_text par bloc
MAX_BLOCKS_PER_CALL = 100    # blocs par appel à blocks.children.append
MAX_TITLE_LENGTH = 200       # longueur max d'une 1re ligne utilisée comme titre


# ---------------------------------------------------------------------------
# Conversion Markdown -> rich text Notion
# ---------------------------------------------------------------------------

DEFAULT_ANNOTATIONS = {
    "bold": False,
    "italic": False,
    "strikethrough": False,
    "underline": False,
    "code": False,
}

INLINE_RE = re.compile(
    r"(?P<code>`[^`\n]+`)"
    r"|(?P<link>\[(?P<link_text>[^\]]*)\]\((?P<link_url>[^)\s]+)\))"
    r"|(?P<bold>\*\*(?P<bold_text>.+?)\*\*)"
    r"|(?P<bold_alt>__(?P<bold_alt_text>.+?)__)"
    r"|(?P<strike>~~(?P<strike_text>.+?)~~)"
    r"|(?P<italic>(?<![\w*])\*(?P<italic_text>[^*\n]+)\*(?![\w*]))"
    r"|(?P<italic_alt>(?<![\w_])_(?P<italic_alt_text>[^_\n]+)_(?![\w_]))"
    r"|(?P<autolink>https?://[^\s<>()\[\]]+)",
    re.DOTALL,
)


def _text_object(content: str, annotations: dict, url: str | None = None) -> dict:
    """Construit un objet rich_text Notion."""
    text: dict = {"content": content}
    if url:
        text["link"] = {"url": url}
    obj: dict = {"type": "text", "text": text}
    active = {k: v for k, v in annotations.items() if v}
    if active:
        obj["annotations"] = {**DEFAULT_ANNOTATIONS, **active}
    return obj


def _split_long(content: str) -> list[str]:
    """Découpe un texte trop long pour un seul objet rich_text Notion."""
    if len(content) <= MAX_TEXT_LENGTH:
        return [content]
    return [
        content[i:i + MAX_TEXT_LENGTH]
        for i in range(0, len(content), MAX_TEXT_LENGTH)
    ]


def parse_inline(text: str, annotations: dict | None = None) -> list[dict]:
    """Convertit du Markdown inline en tableau de rich_text Notion."""
    annotations = annotations or {}
    if not text:
        return []

    parts: list[dict] = []
    cursor = 0

    def flush(raw: str, url: str | None = None):
        for chunk in _split_long(raw):
            if chunk:
                parts.append(_text_object(chunk, annotations, url))

    for match in INLINE_RE.finditer(text):
        if match.start() > cursor:
            flush(text[cursor:match.start()])
        cursor = match.end()

        if match.group("code"):
            for chunk in _split_long(match.group("code")[1:-1]):
                parts.append(_text_object(chunk, {**annotations, "code": True}))
        elif match.group("link"):
            label = match.group("link_text") or match.group("link_url")
            for chunk in _split_long(label):
                parts.append(_text_object(chunk, annotations, match.group("link_url")))
        elif match.group("bold"):
            parts.extend(parse_inline(match.group("bold_text"), {**annotations, "bold": True}))
        elif match.group("bold_alt"):
            parts.extend(parse_inline(match.group("bold_alt_text"), {**annotations, "bold": True}))
        elif match.group("strike"):
            parts.extend(parse_inline(match.group("strike_text"), {**annotations, "strikethrough": True}))
        elif match.group("italic"):
            parts.extend(parse_inline(match.group("italic_text"), {**annotations, "italic": True}))
        elif match.group("italic_alt"):
            parts.extend(parse_inline(match.group("italic_alt_text"), {**annotations, "italic": True}))
        elif match.group("autolink"):
            url = match.group("autolink")
            parts.append(_text_object(url, annotations, url))

    if cursor < len(text):
        flush(text[cursor:])

    return parts[:MAX_RICH_TEXT_ITEMS]


# ---------------------------------------------------------------------------
# Conversion Markdown -> blocs Notion
# ---------------------------------------------------------------------------

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
BULLET_RE = re.compile(r"^\s*[-*+•]\s+(.*)$")
NUMBERED_RE = re.compile(r"^\s*\d+[.)]\s+(.*)$")
TODO_RE = re.compile(r"^\s*(?:[-*+]\s+)?\[([ xX])\]\s+(.*)$")
APPLE_TODO_RE = re.compile(r"^\s*([☐☑✓✔])\s*(.*)$")
QUOTE_RE = re.compile(r"^\s*>\s?(.*)$")
DIVIDER_RE = re.compile(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$")
FENCE_RE = re.compile(r"^\s*```\s*(\w+)?\s*$")
TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
TABLE_SEP_RE = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
IMAGE_RE = re.compile(r"^\s*!\[[^\]]*\]\(([^)\s]+)\)\s*$")

NOTION_CODE_LANGUAGES = {
    "bash", "c", "c++", "c#", "css", "diff", "docker", "go", "graphql", "html",
    "java", "javascript", "json", "kotlin", "markdown", "php", "python", "ruby",
    "rust", "shell", "sql", "swift", "typescript", "xml", "yaml",
}
LANGUAGE_ALIASES = {
    "js": "javascript", "ts": "typescript", "py": "python", "sh": "shell",
    "zsh": "shell", "yml": "yaml", "md": "markdown", "dockerfile": "docker",
}


def _block(block_type: str, payload: dict) -> dict:
    return {"object": "block", "type": block_type, block_type: payload}


def _table_cells(line: str, width: int) -> list[list[dict]]:
    """Découpe une ligne de tableau Markdown en cellules rich_text."""
    raw = line.strip().strip("|").split("|")
    cells = [parse_inline(cell.strip()) for cell in raw[:width]]
    while len(cells) < width:
        cells.append([])
    return cells


def markdown_to_blocks(markdown: str) -> tuple[list[dict], list[str]]:
    """Convertit du Markdown en blocs Notion.

    Retourne (blocs, pièces jointes locales non migrables).
    """
    blocks: list[dict] = []
    attachments: list[str] = []
    lines = markdown.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        if not line.strip():
            i += 1
            continue

        # Bloc de code délimité par ```
        fence = FENCE_RE.match(line)
        if fence:
            language = (fence.group(1) or "plain text").lower()
            language = LANGUAGE_ALIASES.get(language, language)
            if language not in NOTION_CODE_LANGUAGES:
                language = "plain text"
            i += 1
            code_lines = []
            while i < len(lines) and not FENCE_RE.match(lines[i]):
                code_lines.append(lines[i])
                i += 1
            i += 1  # fermeture de la clôture
            code = "\n".join(code_lines)
            blocks.append(_block("code", {
                "rich_text": [_text_object(c, {}) for c in _split_long(code)] or [_text_object("", {})],
                "language": language,
            }))
            continue

        # Tableau Markdown
        if TABLE_ROW_RE.match(line) and i + 1 < len(lines) and TABLE_SEP_RE.match(lines[i + 1]):
            header = line
            width = len([c for c in header.strip().strip("|").split("|")])
            rows = [header]
            i += 2  # en-tête + séparateur
            while i < len(lines) and TABLE_ROW_RE.match(lines[i]):
                rows.append(lines[i])
                i += 1
            blocks.append(_block("table", {
                "table_width": width,
                "has_column_header": True,
                "has_row_header": False,
                "children": [
                    _block("table_row", {"cells": _table_cells(row, width)})
                    for row in rows
                ],
            }))
            continue

        if DIVIDER_RE.match(line):
            blocks.append(_block("divider", {}))
            i += 1
            continue

        image = IMAGE_RE.match(line)
        if image:
            url = image.group(1)
            if url.startswith(("http://", "https://")):
                blocks.append(_block("image", {"type": "external", "external": {"url": url}}))
            else:
                # Une pièce jointe locale ne peut pas être poussée via cette API :
                # on garde une trace lisible dans la page Notion.
                attachments.append(url)
                blocks.append(_block("callout", {
                    "rich_text": parse_inline(f"Pièce jointe non migrée : `{url}`"),
                    "icon": {"type": "emoji", "emoji": "📎"},
                }))
            i += 1
            continue

        heading = HEADING_RE.match(line)
        if heading:
            level = min(len(heading.group(1)), 3)
            blocks.append(_block(f"heading_{level}", {
                "rich_text": parse_inline(heading.group(2).strip()),
            }))
            i += 1
            continue

        todo = TODO_RE.match(line)
        if todo:
            blocks.append(_block("to_do", {
                "rich_text": parse_inline(todo.group(2).strip()),
                "checked": todo.group(1).lower() == "x",
            }))
            i += 1
            continue

        apple_todo = APPLE_TODO_RE.match(line)
        if apple_todo:
            blocks.append(_block("to_do", {
                "rich_text": parse_inline(apple_todo.group(2).strip()),
                "checked": apple_todo.group(1) in "☑✓✔",
            }))
            i += 1
            continue

        quote = QUOTE_RE.match(line)
        if quote:
            quote_lines = [quote.group(1)]
            i += 1
            while i < len(lines) and QUOTE_RE.match(lines[i]):
                quote_lines.append(QUOTE_RE.match(lines[i]).group(1))
                i += 1
            blocks.append(_block("quote", {"rich_text": parse_inline("\n".join(quote_lines).strip())}))
            continue

        bullet = BULLET_RE.match(line)
        if bullet:
            blocks.append(_block("bulleted_list_item", {"rich_text": parse_inline(bullet.group(1).strip())}))
            i += 1
            continue

        numbered = NUMBERED_RE.match(line)
        if numbered:
            blocks.append(_block("numbered_list_item", {"rich_text": parse_inline(numbered.group(1).strip())}))
            i += 1
            continue

        # Paragraphe : on regroupe les lignes consécutives
        paragraph = [line.strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and not _starts_new_block(lines[i]):
            paragraph.append(lines[i].strip())
            i += 1
        blocks.append(_block("paragraph", {"rich_text": parse_inline("\n".join(paragraph))}))

    return blocks, attachments


def _starts_new_block(line: str) -> bool:
    """Vrai si la ligne ouvre un bloc autre qu'un paragraphe."""
    return bool(
        HEADING_RE.match(line) or BULLET_RE.match(line) or NUMBERED_RE.match(line)
        or TODO_RE.match(line) or APPLE_TODO_RE.match(line) or QUOTE_RE.match(line)
        or DIVIDER_RE.match(line) or FENCE_RE.match(line) or TABLE_ROW_RE.match(line)
        or IMAGE_RE.match(line)
    )


# ---------------------------------------------------------------------------
# Lecture de l'export Apple Notes
# ---------------------------------------------------------------------------

FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_front_matter(text: str) -> tuple[dict, str]:
    """Extrait un éventuel front-matter YAML simple (clé: valeur)."""
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return {}, text

    meta: dict = {}
    for raw_line in match.group(1).split("\n"):
        if ":" not in raw_line or raw_line.strip().startswith("#"):
            continue
        key, _, value = raw_line.partition(":")
        value = value.strip().strip('"').strip("'")
        key = key.strip().lower()
        if not key:
            continue
        if value.startswith("[") and value.endswith("]"):
            meta[key] = [v.strip().strip('"').strip("'") for v in value[1:-1].split(",") if v.strip()]
        else:
            meta[key] = value
    return meta, text[match.end():]


def split_title_and_body(text: str, fallback: str) -> tuple[str, str]:
    """Détermine le titre de la note et retourne le corps restant.

    Apple Notes utilise la première ligne comme titre : on la retire du corps
    pour éviter de la répéter dans la page Notion.
    """
    lines = text.split("\n")
    for index, line in enumerate(lines):
        if not line.strip():
            continue
        heading = HEADING_RE.match(line)
        if heading and heading.group(2).strip():
            return heading.group(2).strip(), "\n".join(lines[index + 1:])
        stripped = line.strip()
        if len(stripped) <= MAX_TITLE_LENGTH and not _starts_new_block(line):
            return stripped, "\n".join(lines[index + 1:])
        break
    return fallback, text


@dataclass
class Note:
    path: Path
    relative_path: str
    folder: str
    title: str
    body: str
    meta: dict = field(default_factory=dict)
    modified: str = ""

    @property
    def fingerprint(self) -> str:
        payload = f"{self.title}\n{self.body}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()


def read_notes(source_dir: Path) -> list[Note]:
    """Lit récursivement les fichiers de l'export Apple Notes."""
    notes: list[Note] = []
    for path in sorted(source_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in NOTE_EXTENSIONS:
            continue
        if path.name.startswith(".") or path.name.lower() in SKIPPED_FILENAMES:
            continue

        raw = path.read_text(encoding="utf-8", errors="replace")
        meta, body = parse_front_matter(raw)
        title, body = split_title_and_body(body, path.stem)
        title = str(meta.get("title") or title).strip() or path.stem
        relative = path.relative_to(source_dir)
        folder = str(relative.parent) if str(relative.parent) != "." else ""
        modified = str(meta.get("modified") or meta.get("created") or meta.get("date") or "")
        if not modified:
            modified = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).strftime("%Y-%m-%d")

        notes.append(Note(
            path=path,
            relative_path=str(relative),
            folder=folder,
            title=title,
            body=body.strip("\n"),
            meta=meta,
            modified=modified[:10],
        ))
    return notes


# ---------------------------------------------------------------------------
# Etat local (idempotence)
# ---------------------------------------------------------------------------

def load_state(state_file: Path) -> dict:
    state = {}
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"  Etat illisible ({state_file.name}), il sera recréé.")
    if not isinstance(state.get("notes"), dict):
        state["notes"] = {}
    return state


def save_state(state_file: Path, state: dict):
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Ecriture vers Notion
# ---------------------------------------------------------------------------

def display_path(path: Path) -> str:
    """Chemin relatif au dépôt quand c'est possible, absolu sinon."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def chunked(items: list, size: int):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def build_properties(schema: dict, title_property: str, note: Note, mapping: dict) -> dict:
    """Construit les propriétés Notion à partir de la note et du mapping config."""
    properties = {title_property: {"title": [_text_object(note.title[:MAX_TEXT_LENGTH], {})]}}
    values = {
        "folder": note.folder or "Sans dossier",
        "source": "Apple Notes",
        "path": note.relative_path,
        "modified": note.modified,
    }

    for key, prop_name in mapping.items():
        prop = schema.get(prop_name)
        value = values.get(key) or note.meta.get(key)
        if not prop or not value:
            continue
        prop_type = prop.get("type")
        if prop_type == "select":
            properties[prop_name] = {"select": {"name": str(value)[:100]}}
        elif prop_type == "multi_select":
            items = value if isinstance(value, list) else [value]
            properties[prop_name] = {"multi_select": [{"name": str(v)[:100]} for v in items]}
        elif prop_type == "rich_text":
            properties[prop_name] = {"rich_text": [_text_object(str(value)[:MAX_TEXT_LENGTH], {})]}
        elif prop_type == "date":
            properties[prop_name] = {"date": {"start": str(value)}}
        elif prop_type == "url":
            properties[prop_name] = {"url": str(value)}
    return properties


def append_blocks(notion, page_id: str, blocks: list[dict]):
    for batch in chunked(blocks, MAX_BLOCKS_PER_CALL):
        notion.blocks.children.append(block_id=page_id, children=batch)


def clear_blocks(notion, page_id: str):
    """Supprime le contenu existant d'une page avant réécriture."""
    cursor = None
    block_ids = []
    while True:
        response = notion.blocks.children.list(block_id=page_id, start_cursor=cursor)
        block_ids.extend(b["id"] for b in response.get("results", []))
        if not response.get("has_more"):
            break
        cursor = response.get("next_cursor")
    for block_id in block_ids:
        notion.blocks.delete(block_id=block_id)


# ---------------------------------------------------------------------------
# Rapport et historique
# ---------------------------------------------------------------------------

def update_history(created: int, updated: int, skipped: int, target_label: str):
    today = datetime.now().strftime("%Y-%m-%d")
    entry = (
        f"\n## {today}\n\n### Migration Apple Notes vers Notion\n"
        f"- Cible : {target_label}\n"
        f"- Pages créées : {created}\n"
        f"- Pages mises à jour : {updated}\n"
        f"- Notes inchangées ignorées : {skipped}\n"
    )
    if HISTORY_FILE.exists():
        existing = HISTORY_FILE.read_text(encoding="utf-8")
        header_end = existing.find("\n## ")
        new_content = existing + entry if header_end == -1 else existing[:header_end] + entry + existing[header_end:]
    else:
        new_content = "# HISTORY.md\n" + entry
    HISTORY_FILE.write_text(new_content, encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def load_config(config_file: Path) -> dict:
    if not config_file.exists():
        print(f"Fichier de config manquant : {config_file}")
        sys.exit(1)
    config = json.loads(config_file.read_text(encoding="utf-8"))
    return config.get("apple_notes", {})


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Migre un export Apple Notes vers Notion.")
    parser.add_argument("--source", help="Dossier de l'export Apple Notes")
    parser.add_argument("--config", default=str(CONFIG_FILE), help="Fichier de configuration")
    parser.add_argument("--database", help="ID de la base Notion cible (prioritaire sur la config)")
    parser.add_argument("--parent-page", help="ID de la page Notion parente (mode page)")
    parser.add_argument("--limit", type=int, help="Ne traiter que les N premières notes")
    parser.add_argument("--force", action="store_true", help="Repousser même les notes inchangées")
    parser.add_argument("--dry-run", action="store_true", help="Simuler sans écrire dans Notion")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    config = load_config(Path(args.config))

    source_dir = Path(args.source or config.get("source", DEFAULT_SOURCE))
    if not source_dir.is_absolute():
        source_dir = ROOT / source_dir

    if not source_dir.exists():
        print(f"Dossier source introuvable : {source_dir}")
        print("Déposer l'export Apple Notes puis relancer. Voir le README du dossier.")
        return 1

    notes = read_notes(source_dir)
    if args.limit:
        notes = notes[:args.limit]
    if not notes:
        print(f"Aucune note trouvée dans {source_dir} (extensions acceptées : {', '.join(NOTE_EXTENSIONS)}).")
        return 1

    target = config.get("target", {})
    database_id = args.database or (target.get("id") if target.get("type") == "database" else None)
    parent_page_id = args.parent_page or (target.get("id") if target.get("type") == "page" else None)
    if database_id and "REMPLACER" in database_id:
        database_id = None
    if parent_page_id and "REMPLACER" in parent_page_id:
        parent_page_id = None

    print(f"Export lu : {len(notes)} note(s) dans {display_path(source_dir)}\n")

    state_file = Path(config.get("state_file", STATE_FILE))
    if not state_file.is_absolute():
        state_file = ROOT / state_file
    state = load_state(state_file)

    # --- Mode simulation : aucune dépendance ni jeton nécessaire ---
    if args.dry_run:
        total_blocks = 0
        total_attachments = 0
        for note in notes:
            blocks, attachments = markdown_to_blocks(note.body)
            total_blocks += len(blocks)
            total_attachments += len(attachments)
            status = "inchangée" if state["notes"].get(note.relative_path, {}).get("fingerprint") == note.fingerprint else "à migrer"
            folder = f"[{note.folder}] " if note.folder else ""
            print(f"  {folder}{note.title} — {len(blocks)} bloc(s), {status}")
        print(f"\nSimulation : {len(notes)} note(s), {total_blocks} bloc(s) Notion, "
              f"{total_attachments} pièce(s) jointe(s) locale(s) non migrable(s).")
        print(f"Cible : {'base ' + database_id if database_id else 'page ' + parent_page_id if parent_page_id else 'NON CONFIGURÉE'}")
        return 0

    # --- Migration réelle ---
    if not database_id and not parent_page_id:
        print("Cible Notion non configurée.")
        print("Renseigner apple_notes.target.id dans notion-config.json, "
              "ou passer --database / --parent-page.")
        return 1

    try:
        from notion_client import Client
        from dotenv import load_dotenv
    except ImportError:
        print("Dépendances manquantes. Lancer : pip install notion-client python-dotenv")
        return 1

    load_dotenv()
    token = os.getenv("NOTION_TOKEN")
    if not token:
        print("Erreur : variable NOTION_TOKEN manquante.")
        print("Créer un fichier .env à la racine avec : NOTION_TOKEN=secret_xxxx")
        return 1

    notion = Client(auth=token)
    mapping = config.get("properties", {})

    if database_id:
        schema = notion.databases.retrieve(database_id=database_id).get("properties", {})
        title_property = next((n for n, p in schema.items() if p.get("type") == "title"), None)
        if not title_property:
            print(f"Aucune propriété titre dans la base {database_id}.")
            return 1
        target_label = f"base Notion {database_id}"
    else:
        schema, title_property = {}, "title"
        target_label = f"page Notion {parent_page_id}"

    created = updated = skipped = 0
    attachments_total: list[str] = []
    failures: list[tuple[str, str]] = []

    for note in notes:
        known = state["notes"].get(note.relative_path, {})
        if known.get("fingerprint") == note.fingerprint and not args.force:
            skipped += 1
            continue

        blocks, attachments = markdown_to_blocks(note.body)
        attachments_total.extend(attachments)
        first_batch, rest = blocks[:MAX_BLOCKS_PER_CALL], blocks[MAX_BLOCKS_PER_CALL:]

        try:
            page_id = known.get("page_id")
            if page_id:
                clear_blocks(notion, page_id)
                if database_id:
                    notion.pages.update(
                        page_id=page_id,
                        properties=build_properties(schema, title_property, note, mapping),
                    )
                append_blocks(notion, page_id, blocks)
                updated += 1
                print(f"  Mise à jour : {note.title}")
            else:
                if database_id:
                    page = notion.pages.create(
                        parent={"database_id": database_id},
                        properties=build_properties(schema, title_property, note, mapping),
                        children=first_batch,
                    )
                else:
                    page = notion.pages.create(
                        parent={"page_id": parent_page_id},
                        properties={"title": [_text_object(note.title[:MAX_TEXT_LENGTH], {})]},
                        children=first_batch,
                    )
                page_id = page["id"]
                if rest:
                    append_blocks(notion, page_id, rest)
                created += 1
                print(f"  Créée : {note.title}")

            state["notes"][note.relative_path] = {
                "page_id": page_id,
                "fingerprint": note.fingerprint,
                "title": note.title,
                "synced_at": datetime.now(timezone.utc).isoformat(),
            }
            save_state(state_file, state)
        except Exception as exc:  # l'API Notion lève des erreurs très variées
            failures.append((note.relative_path, str(exc)))
            print(f"  ECHEC : {note.title} — {exc}")

    save_state(state_file, state)

    print(f"\nMigration terminée vers {target_label}.")
    print(f"  Créées : {created} | Mises à jour : {updated} | Ignorées (inchangées) : {skipped}")
    if attachments_total:
        print(f"  Pièces jointes locales signalées dans les pages : {len(attachments_total)}")
    if failures:
        print(f"  Echecs : {len(failures)}")
        for path, error in failures:
            print(f"    - {path} : {error}")

    if created or updated:
        update_history(created, updated, skipped, target_label)

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
