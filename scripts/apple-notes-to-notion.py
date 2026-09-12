#!/usr/bin/env python3
"""
Archive les notes Apple (texte + photos) dans une base de données Notion.

Pipeline (à exécuter sur le Mac, pas sur une machine distante) :
  1. AppleScript liste les notes de Notes.app et leur date de modification
  2. On compare avec l'état local pour ne traiter que les notes nouvelles ou modifiées
  3. AppleScript exporte le corps HTML et les pièces jointes de ces notes
  4. Le HTML est converti en blocs Notion, les photos sont envoyées via l'API d'upload
  5. Une page est créée ou mise à jour dans la base Notion

Usage :
  python3 scripts/apple-notes-to-notion.py                 # sync incrémentale
  python3 scripts/apple-notes-to-notion.py --full          # repousse toutes les notes
  python3 scripts/apple-notes-to-notion.py --limit 5       # test sur 5 notes
  python3 scripts/apple-notes-to-notion.py --dry-run       # rien n'est écrit dans Notion
  python3 scripts/apple-notes-to-notion.py --create-db     # crée la base puis affiche son id

Prérequis :
  pip3 install requests python-dotenv
  .env avec NOTION_TOKEN et NOTION_NOTES_DB_ID (ou NOTION_NOTES_PARENT_PAGE_ID pour --create-db)
  Autorisation Automatisation > Notes pour le terminal utilisé
"""

import argparse
import hashlib
import json
import mimetypes
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

try:
    import requests
    from dotenv import load_dotenv
except ImportError:
    print("Dépendances manquantes. Lancer : pip3 install requests python-dotenv")
    sys.exit(1)

ROOT = Path(__file__).parent.parent
APPLESCRIPT = ROOT / "scripts" / "apple-notes-export.applescript"
STATE_FILE = ROOT / ".apple-notes-state.json"
DEFAULT_EXPORT_DIR = Path.home() / ".cache" / "jarvis-apple-notes"
REPORT_FILE = ROOT / "context" / "import" / "apple-notes-archive.md"

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = os.getenv("NOTION_VERSION", "2022-06-28")
THROTTLE = 0.35           # l'API Notion tolère environ 3 requêtes par seconde
MAX_CHILDREN = 100        # blocs par requête
MAX_RICH_TEXT = 2000      # caractères par fragment de texte
MAX_UPLOAD_BYTES = 20 * 1024 * 1024   # limite d'un upload simple Notion

# Dossiers Notes.app à ne pas archiver (la corbeille est localisée selon la langue du Mac)
EXCLUDED_FOLDERS = {
    f.strip().lower()
    for f in os.getenv(
        "NOTES_EXCLUDE_FOLDERS",
        "Recently Deleted,Suppressions récentes,Supprimés récemment,Corbeille",
    ).split(",")
    if f.strip()
}

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".heif", ".tif", ".tiff", ".bmp"}
CONVERT_EXTS = {".heic", ".heif", ".tif", ".tiff", ".bmp"}   # convertis en JPEG pour l'affichage Notion

load_dotenv(ROOT / ".env")


# ─────────────────────────────────────────────────────────── HTML → blocs Notion

class NotesHTMLParser(HTMLParser):
    """Convertit le HTML produit par Notes.app en blocs Notion.

    Notes.app génère un HTML simple : des <div> pour les paragraphes, des <h1>-<h3>,
    des listes, et du gras/italique/souligné. Les images n'y figurent pas de façon
    exploitable, elles sont récupérées séparément comme pièces jointes.
    """

    BLOCK_TAGS = {"div", "p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote"}
    HEADINGS = {"h1": "heading_1", "h2": "heading_2", "h3": "heading_3",
                "h4": "heading_3", "h5": "heading_3", "h6": "heading_3"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []
        self.spans = []            # fragments (texte, annotations, lien) du bloc courant
        self.block_type = "paragraph"
        self.list_stack = []       # "ul" / "ol" imbriqués
        self.annotations = {"bold": False, "italic": False, "underline": False,
                            "strikethrough": False, "code": False}
        self.link = None
        self.checked = None        # cases à cocher des listes Notes

    # -- gestion des blocs

    def _flush(self):
        text = "".join(s[0] for s in self.spans)
        if text.strip():
            block_type = self.block_type
            payload = {"rich_text": rich_text_from_spans(self.spans)}
            if block_type == "to_do":
                payload["checked"] = bool(self.checked)
            self.blocks.append({"object": "block", "type": block_type, block_type: payload})
        self.spans = []
        self.block_type = "paragraph"
        self.checked = None

    def _current_list_type(self):
        if not self.list_stack:
            return "paragraph"
        return "numbered_list_item" if self.list_stack[-1] == "ol" else "bulleted_list_item"

    # -- callbacks HTMLParser

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "br":
            self.spans.append(("\n", dict(self.annotations), self.link))
        elif tag in ("ul", "ol"):
            self._flush()
            self.list_stack.append(tag)
        elif tag == "li":
            self._flush()
            self.block_type = self._current_list_type()
            cls = attrs.get("class", "")
            if "checkbox" in cls or attrs.get("type") == "checkbox":
                self.block_type = "to_do"
                self.checked = "checked" in cls
        elif tag in self.HEADINGS:
            self._flush()
            self.block_type = self.HEADINGS[tag]
        elif tag == "blockquote":
            self._flush()
            self.block_type = "quote"
        elif tag in ("div", "p"):
            self._flush()
            self.block_type = self._current_list_type() if self.list_stack else "paragraph"
        elif tag in ("b", "strong"):
            self.annotations["bold"] = True
        elif tag in ("i", "em"):
            self.annotations["italic"] = True
        elif tag == "u":
            self.annotations["underline"] = True
        elif tag in ("s", "strike", "del"):
            self.annotations["strikethrough"] = True
        elif tag in ("code", "tt"):
            self.annotations["code"] = True
        elif tag == "a":
            href = attrs.get("href")
            if href and href.startswith(("http://", "https://", "mailto:")):
                self.link = href

    def handle_endtag(self, tag):
        if tag in ("ul", "ol"):
            self._flush()
            if self.list_stack:
                self.list_stack.pop()
        elif tag in self.BLOCK_TAGS:
            self._flush()
        elif tag in ("b", "strong"):
            self.annotations["bold"] = False
        elif tag in ("i", "em"):
            self.annotations["italic"] = False
        elif tag == "u":
            self.annotations["underline"] = False
        elif tag in ("s", "strike", "del"):
            self.annotations["strikethrough"] = False
        elif tag in ("code", "tt"):
            self.annotations["code"] = False
        elif tag == "a":
            self.link = None

    def handle_data(self, data):
        if data:
            self.spans.append((data, dict(self.annotations), self.link))

    def close(self):
        super().close()
        self._flush()


def rich_text_from_spans(spans):
    """Fusionne les fragments contigus de même style et respecte la limite de 2000 caractères."""
    merged = []
    for text, annotations, link in spans:
        if merged and merged[-1][1] == annotations and merged[-1][2] == link:
            merged[-1][0] += text
        else:
            merged.append([text, annotations, link])

    rich = []
    for text, annotations, link in merged:
        for chunk in split_text(text, MAX_RICH_TEXT):
            item = {"type": "text", "text": {"content": chunk}, "annotations": annotations}
            if link:
                item["text"]["link"] = {"url": link}
            rich.append(item)
    return rich[:100]


def split_text(text, size):
    return [text[i:i + size] for i in range(0, len(text), size)] or [""]


def html_to_blocks(html, note_title):
    parser = NotesHTMLParser()
    parser.feed(html)
    parser.close()
    blocks = parser.blocks

    # Notes.app répète le titre en première ligne du corps : on l'enlève pour ne pas le dupliquer.
    if blocks and note_title:
        first = plain_text_of(blocks[0]).strip()
        if first and first == note_title.strip():
            blocks = blocks[1:]
    return blocks


def plain_text_of(block):
    payload = block.get(block.get("type"), {})
    return "".join(rt["text"]["content"] for rt in payload.get("rich_text", []))


# ─────────────────────────────────────────────────────────── client Notion

class Notion:
    def __init__(self, token, dry_run=False):
        self.token = token
        self.dry_run = dry_run
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
        })

    def _request(self, method, url, **kwargs):
        for attempt in range(5):
            response = self.session.request(method, url, timeout=120, **kwargs)
            if response.status_code == 429:
                wait = float(response.headers.get("Retry-After", 2 ** attempt))
                time.sleep(wait)
                continue
            if response.status_code >= 500:
                time.sleep(2 ** attempt)
                continue
            if response.status_code >= 400:
                raise RuntimeError(f"Notion {response.status_code} sur {url} : {response.text[:400]}")
            time.sleep(THROTTLE)
            return response.json() if response.content else {}
        raise RuntimeError(f"Notion injoignable après 5 tentatives : {url}")

    def post(self, path, payload):
        return self._request("POST", f"{NOTION_API}{path}", json=payload)

    def patch(self, path, payload):
        return self._request("PATCH", f"{NOTION_API}{path}", json=payload)

    def delete(self, path):
        return self._request("DELETE", f"{NOTION_API}{path}")

    def get(self, path):
        return self._request("GET", f"{NOTION_API}{path}")

    # -- upload de fichier (API File Upload de Notion)

    def upload_file(self, path: Path):
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        created = self.post("/file_uploads", {"filename": path.name, "content_type": content_type})
        upload_url = created["upload_url"]
        with path.open("rb") as handle:
            response = self.session.post(
                upload_url,
                files={"file": (path.name, handle, content_type)},
                timeout=300,
            )
        if response.status_code >= 400:
            raise RuntimeError(f"Upload refusé pour {path.name} : {response.text[:300]}")
        time.sleep(THROTTLE)
        return created["id"]


# ─────────────────────────────────────────────────────────── base de données Notion

DB_PROPERTIES = {
    "Titre": {"title": {}},
    "Dossier": {"select": {}},
    "Créée le": {"date": {}},
    "Modifiée le": {"date": {}},
    "Photos": {"number": {}},
    "ID Apple": {"rich_text": {}},
    "Source": {"select": {}},
}


def create_database(notion: Notion, parent_page_id: str):
    payload = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "title": [{"type": "text", "text": {"content": "Archives Notes Apple"}}],
        "description": [{"type": "text", "text": {"content": "Notes Apple archivées automatiquement depuis Notes.app."}}],
        "properties": DB_PROPERTIES,
    }
    database = notion.post("/databases", payload)
    return database["id"]


def find_existing_page(notion: Notion, database_id: str, note_id: str):
    payload = {
        "filter": {"property": "ID Apple", "rich_text": {"equals": note_id}},
        "page_size": 1,
    }
    result = notion.post(f"/databases/{database_id}/query", payload)
    results = result.get("results", [])
    return results[0]["id"] if results else None


def clear_page_blocks(notion: Notion, page_id: str):
    cursor = None
    block_ids = []
    while True:
        suffix = f"?start_cursor={cursor}" if cursor else ""
        result = notion.get(f"/blocks/{page_id}/children{suffix}")
        block_ids.extend(block["id"] for block in result.get("results", []))
        if not result.get("has_more"):
            break
        cursor = result.get("next_cursor")
    for block_id in block_ids:
        notion.delete(f"/blocks/{block_id}")


def page_properties(meta, media_count):
    props = {
        "Titre": {"title": [{"type": "text", "text": {"content": (meta.get("title") or "Sans titre")[:200]}}]},
        "ID Apple": {"rich_text": [{"type": "text", "text": {"content": meta["id"][:2000]}}]},
        "Photos": {"number": media_count},
        "Source": {"select": {"name": "Apple Notes"}},
    }
    folder = meta.get("folder")
    if folder:
        props["Dossier"] = {"select": {"name": folder[:100]}}
    if meta.get("created"):
        props["Créée le"] = {"date": {"start": meta["created"]}}
    if meta.get("modified"):
        props["Modifiée le"] = {"date": {"start": meta["modified"]}}
    return props


# ─────────────────────────────────────────────────────────── médias

def prepare_media(media_dir: Path, work_dir: Path):
    """Trie les pièces jointes, convertit ce que Notion affiche mal, écarte ce qui est trop lourd."""
    images, others, problems = [], [], []
    if not media_dir.is_dir():
        return images, others, problems

    for path in sorted(media_dir.iterdir()):
        if not path.is_file() or path.name.startswith("."):
            continue

        prepared = path
        suffix = path.suffix.lower()

        if suffix in CONVERT_EXTS:
            converted = convert_to_jpeg(path, work_dir)
            if converted:
                prepared = converted
                suffix = ".jpg"

        size = prepared.stat().st_size
        if size > MAX_UPLOAD_BYTES:
            shrunk = shrink_image(prepared, work_dir) if suffix in IMAGE_EXTS else None
            if shrunk and shrunk.stat().st_size <= MAX_UPLOAD_BYTES:
                prepared = shrunk
            else:
                problems.append(f"{path.name} ignoré ({size // (1024 * 1024)} Mo, limite 20 Mo)")
                continue

        (images if suffix in IMAGE_EXTS else others).append(prepared)

    return images, others, problems


def convert_to_jpeg(path: Path, work_dir: Path):
    """HEIC et consorts s'affichent mal dans Notion : sips (natif macOS) les convertit en JPEG."""
    if not shutil.which("sips"):
        return None
    work_dir.mkdir(parents=True, exist_ok=True)
    target = work_dir / (path.stem + ".jpg")
    result = subprocess.run(
        ["sips", "-s", "format", "jpeg", str(path), "--out", str(target)],
        capture_output=True, text=True,
    )
    return target if result.returncode == 0 and target.exists() else None


def shrink_image(path: Path, work_dir: Path):
    if not shutil.which("sips"):
        return None
    work_dir.mkdir(parents=True, exist_ok=True)
    target = work_dir / ("reduit-" + path.stem + ".jpg")
    result = subprocess.run(
        ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "70", "-Z", "3000",
         str(path), "--out", str(target)],
        capture_output=True, text=True,
    )
    return target if result.returncode == 0 and target.exists() else None


# ─────────────────────────────────────────────────────────── export AppleScript

def run_applescript(export_dir: Path, mode: str, ids_file: Path = None):
    if sys.platform != "darwin":
        raise RuntimeError(
            "Ce script lit Notes.app : il doit tourner sur ton Mac, pas sur une machine distante."
        )
    command = ["osascript", str(APPLESCRIPT), str(export_dir), mode]
    if ids_file:
        command.append(str(ids_file))
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        stderr = result.stderr.strip()
        if "-1743" in stderr or "not allowed" in stderr.lower():
            raise RuntimeError(
                "Accès à Notes.app refusé. Autoriser le terminal dans Réglages Système > "
                "Confidentialité et sécurité > Automatisation > Notes, puis relancer."
            )
        raise RuntimeError(f"AppleScript en échec : {stderr[:500]}")
    return result.stdout.strip()


def read_index(export_dir: Path):
    index_path = export_dir / "index.tsv"
    if not index_path.exists():
        return []
    notes = []
    for line in index_path.read_text(encoding="utf-8").splitlines():
        fields = line.split("\t")
        if len(fields) < 6:
            continue
        notes.append({
            "id": fields[0],
            "modified": fields[1],
            "created": fields[2],
            "folder": fields[3],
            "title": fields[4],
            "locked": fields[5].lower() == "true",
        })
    return notes


def read_meta(note_dir: Path):
    meta = {}
    meta_path = note_dir / "meta.tsv"
    if meta_path.exists():
        for line in meta_path.read_text(encoding="utf-8").splitlines():
            if "\t" in line:
                key, value = line.split("\t", 1)
                meta[key] = value
    return meta


def note_dir_name(note_id: str):
    """Reproduit le nom de dossier généré par l'AppleScript."""
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-")
    slug = "".join(c if c in allowed else "-" for c in note_id)
    return slug[-80:]


# ─────────────────────────────────────────────────────────── état local

def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print("État local illisible, il sera reconstruit.")
    return {"last_sync": None, "notes": {}}


def save_state(state):
    state["last_sync"] = datetime.now().isoformat(timespec="seconds")
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def content_fingerprint(html, media_paths):
    digest = hashlib.sha256()
    digest.update(html.encode("utf-8"))
    for path in media_paths:
        digest.update(path.name.encode("utf-8"))
        digest.update(str(path.stat().st_size).encode("utf-8"))
    return digest.hexdigest()


# ─────────────────────────────────────────────────────────── archivage d'une note

def archive_note(notion: Notion, database_id: str, note_dir: Path, work_dir: Path, state,
                 dry_run, force=False):
    meta = read_meta(note_dir)
    if not meta.get("id"):
        return None

    html = (note_dir / "body.html").read_text(encoding="utf-8") if (note_dir / "body.html").exists() else ""
    images, others, problems = prepare_media(note_dir / "media", work_dir / note_dir.name)
    media_paths = images + others

    blocks = html_to_blocks(html, meta.get("title", ""))

    if dry_run:
        return {
            "id": meta["id"], "title": meta.get("title", ""), "blocks": len(blocks),
            "images": len(images), "files": len(others), "problems": problems, "action": "simulation",
        }

    known = state["notes"].get(meta["id"], {})
    fingerprint = content_fingerprint(html, media_paths)

    # Ouvrir une note dans Notes.app suffit parfois à changer sa date de modification :
    # si le contenu est identique au dernier archivage, rien à repousser.
    if not force and known.get("page_id") and known.get("fingerprint") == fingerprint:
        known["modified"] = meta.get("modified", "")
        known["synced_at"] = datetime.now().isoformat(timespec="seconds")
        return {
            "id": meta["id"], "title": meta.get("title", ""), "blocks": len(blocks),
            "images": len(images), "files": len(others), "problems": problems,
            "action": "inchangée",
        }

    page_id = known.get("page_id") or find_existing_page(notion, database_id, meta["id"])
    action = "mise à jour" if page_id else "création"

    if page_id:
        clear_page_blocks(notion, page_id)
        notion.patch(f"/pages/{page_id}", {"properties": page_properties(meta, len(images))})
    else:
        page = notion.post("/pages", {
            "parent": {"database_id": database_id},
            "properties": page_properties(meta, len(images)),
        })
        page_id = page["id"]

    # Le corps d'abord, les pièces jointes ensuite : AppleScript ne donne pas leur
    # position exacte dans le texte, on les regroupe donc sous un titre dédié.
    children = list(blocks)
    if media_paths:
        children.append({
            "object": "block", "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Photos et pièces jointes"}}]},
        })

    append_children(notion, page_id, children)

    uploaded = 0
    for path in media_paths:
        try:
            upload_id = notion.upload_file(path)
        except RuntimeError as error:
            problems.append(f"{path.name} : {error}")
            continue
        block_type = "image" if path.suffix.lower() in IMAGE_EXTS else "file"
        append_children(notion, page_id, [{
            "object": "block", "type": block_type,
            block_type: {"type": "file_upload", "file_upload": {"id": upload_id}},
        }])
        uploaded += 1

    state["notes"][meta["id"]] = {
        "page_id": page_id,
        "title": meta.get("title", ""),
        "modified": meta.get("modified", ""),
        "fingerprint": fingerprint,
        "media": uploaded,
        "synced_at": datetime.now().isoformat(timespec="seconds"),
    }

    return {
        "id": meta["id"], "title": meta.get("title", ""), "blocks": len(blocks),
        "images": len(images), "files": len(others), "problems": problems, "action": action,
    }


def append_children(notion: Notion, page_id: str, children):
    for start in range(0, len(children), MAX_CHILDREN):
        batch = children[start:start + MAX_CHILDREN]
        if batch:
            notion.patch(f"/blocks/{page_id}/children", {"children": batch})


# ─────────────────────────────────────────────────────────── rapport

def write_report(results, skipped_locked, state):
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# Archives Notes Apple",
        "",
        f"Dernière synchronisation : {now}",
        f"Notes archivées au total : {len(state['notes'])}",
        "",
        "## Dernière passe",
        "",
    ]
    changed = [r for r in results if r["action"] != "inchangée"]
    if changed:
        for item in changed:
            photos = f", {item['images']} photo(s)" if item["images"] else ""
            lines.append(f"- {item['title'] or 'Sans titre'} ({item['action']}{photos})")
    else:
        lines.append("- Aucune note nouvelle ou modifiée")
    unchanged = len(results) - len(changed)
    if unchanged:
        lines += ["", f"Notes revues sans changement de contenu : {unchanged}"]
    if skipped_locked:
        lines += ["", f"Notes verrouillées ignorées : {skipped_locked} (à déverrouiller dans Notes.app pour les archiver)"]
    problems = [p for item in results for p in item["problems"]]
    if problems:
        lines += ["", "## Points d'attention", ""] + [f"- {p}" for p in problems]
    REPORT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ─────────────────────────────────────────────────────────── programme principal

def main():
    parser = argparse.ArgumentParser(description="Archive les notes Apple dans Notion.")
    parser.add_argument("--full", action="store_true", help="repousse toutes les notes, même inchangées")
    parser.add_argument("--limit", type=int, help="ne traite que les N premières notes à synchroniser")
    parser.add_argument("--dry-run", action="store_true", help="n'écrit rien dans Notion")
    parser.add_argument("--create-db", action="store_true", help="crée la base Notion puis affiche son id")
    parser.add_argument("--export-dir", type=Path, default=DEFAULT_EXPORT_DIR, help="dossier de travail")
    args = parser.parse_args()

    token = os.getenv("NOTION_TOKEN")
    if not token:
        print("Erreur : NOTION_TOKEN manquant dans .env")
        return 1

    notion = Notion(token, dry_run=args.dry_run)

    if args.create_db:
        parent = os.getenv("NOTION_NOTES_PARENT_PAGE_ID")
        if not parent:
            print("Erreur : NOTION_NOTES_PARENT_PAGE_ID manquant dans .env")
            print("Prendre l'id dans l'URL de la page Notion qui hébergera la base, et partager")
            print("cette page avec ton intégration Notion.")
            return 1
        try:
            database_id = create_database(notion, parent)
        except RuntimeError as error:
            print(f"Erreur : {error}")
            return 1
        print(f"Base créée. Ajouter dans .env :\n  NOTION_NOTES_DB_ID={database_id}")
        return 0

    database_id = os.getenv("NOTION_NOTES_DB_ID")
    if not database_id and not args.dry_run:
        print("Erreur : NOTION_NOTES_DB_ID manquant dans .env")
        print("Lancer d'abord : python3 scripts/apple-notes-to-notion.py --create-db")
        return 1

    export_dir = args.export_dir
    export_dir.mkdir(parents=True, exist_ok=True)
    work_dir = export_dir / "converti"

    state = load_state()

    print("Lecture de Notes.app...")
    try:
        run_applescript(export_dir, "list")
    except RuntimeError as error:
        print(f"Erreur : {error}")
        return 1
    notes = read_index(export_dir)
    kept, excluded = [], 0
    for note in notes:
        if note["folder"].strip().lower() in EXCLUDED_FOLDERS:
            excluded += 1
        else:
            kept.append(note)
    notes = kept
    locked = [n for n in notes if n["locked"]]
    print(f"{len(notes)} note(s) trouvée(s), dont {len(locked)} verrouillée(s).")
    if excluded:
        print(f"{excluded} note(s) ignorée(s) (corbeille ou dossier exclu).")

    to_sync = []
    for note in notes:
        if note["locked"]:
            continue
        known = state["notes"].get(note["id"])
        if args.full or not known or known.get("modified") != note["modified"]:
            to_sync.append(note)

    if args.limit:
        to_sync = to_sync[:args.limit]

    if not to_sync:
        print("Aucune note nouvelle ou modifiée.")
        write_report([], len(locked), state)
        save_state(state)
        return 0

    print(f"{len(to_sync)} note(s) à archiver. Export du contenu et des photos...")
    ids_file = export_dir / "wanted-ids.txt"
    ids_file.write_text("\n".join(n["id"] for n in to_sync), encoding="utf-8")
    try:
        run_applescript(export_dir, "export", ids_file)
    except RuntimeError as error:
        print(f"Erreur : {error}")
        return 1

    results = []
    for position, note in enumerate(to_sync, start=1):
        directory = export_dir / "notes" / note_dir_name(note["id"])
        if not directory.exists():
            print(f"  [{position}/{len(to_sync)}] {note['title']} : contenu non exporté, ignorée")
            continue
        try:
            result = archive_note(notion, database_id, directory, work_dir, state,
                                  args.dry_run, force=args.full)
        except RuntimeError as error:
            print(f"  [{position}/{len(to_sync)}] {note['title']} : échec ({error})")
            save_state(state)
            continue
        if result:
            results.append(result)
            photos = f" + {result['images']} photo(s)" if result["images"] else ""
            print(f"  [{position}/{len(to_sync)}] {result['title'] or 'Sans titre'} : {result['action']}{photos}")

    if not args.dry_run:
        save_state(state)
        write_report(results, len(locked), state)
        print(f"\nTerminé. Rapport : {REPORT_FILE.relative_to(ROOT)}")
    else:
        print("\nSimulation terminée, rien n'a été écrit dans Notion.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
