#!/usr/bin/env python3
"""
Archive les conversations ChatGPT vers Markdown local + base Notion.

Source de verite : l'export officiel OpenAI
(ChatGPT > Reglages > Controle des donnees > Exporter les donnees).
Le ZIP recu par mail contient conversations.json, seul export exhaustif :
tous les messages, non tronques, avec horodatage et pieces jointes.

Pipeline :
    conversations.json  ->  fil principal  ->  Markdown local
                                           ->  classification par tags
                                           ->  Notion (dedup par URL)

Usage :
    # 1. Analyser sans rien ecrire
    python3 scripts/archive-chatgpt.py --export ~/Downloads/export.zip --dry-run

    # 2. Ecrire seulement les Markdown locaux
    python3 scripts/archive-chatgpt.py --export ~/Downloads/export.zip --local

    # 3. Markdown local + creation/reparation des pages Notion
    python3 scripts/archive-chatgpt.py --export ~/Downloads/export.zip --push

    # 4. Reclasser les pages Notion existantes (tags seulement, contenu intact)
    python3 scripts/archive-chatgpt.py --export ~/Downloads/export.zip --tags-only

Requiert pour --push / --tags-only :
    pip install notion-client python-dotenv
    NOTION_TOKEN dans .env a la racine du projet.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import unicodedata
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = ROOT / "notion-config.json"
TAXONOMY_FILE = ROOT / "chatgpt-taxonomy.json"
ARCHIVE_DIR = ROOT / "context" / "import" / "chatgpt-archives"
REPORT_FILE = ARCHIVE_DIR / "_rapport-import.md"

EXPORT_VERSION = "openai-export-v1"
CHAT_URL = "https://chatgpt.com/c/{}"

# Limites API Notion (developers.notion.com/reference/request-limits)
MAX_RICH_TEXT = 2000        # caracteres par objet rich_text
MAX_BLOCKS_PER_CALL = 100   # blocs par requete
MAX_PAYLOAD_BYTES = 400_000  # marge sous la limite de 500 Ko par requete
MAX_SEGMENTS_PER_BLOCK = 8  # -> 16 000 caracteres max par bloc
REQ_PER_SECOND = 3
WINDOW_BUDGET = 850         # marge sous les 1000 req / 5 min par workspace

ROLE_LABEL = {"user": "Njaho", "assistant": "ChatGPT", "tool": "Outil", "system": "Systeme"}


# --------------------------------------------------------------------------
# Utilitaires
# --------------------------------------------------------------------------

def strip_accents(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


def normalize(text: str) -> str:
    """Minuscules sans accents, pour la recherche de mots-cles."""
    return strip_accents(text).lower()


def slugify(text: str, maxlen: int = 60) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", normalize(text)).strip("-")
    return (slug[:maxlen].rstrip("-") or "sans-titre")


def ts_to_dt(value) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromtimestamp(float(value), tz=timezone.utc)
    except (TypeError, ValueError, OSError):
        return None


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------------------
# Lecture de l'export OpenAI
# --------------------------------------------------------------------------

def read_export(path: Path) -> list[dict]:
    """Accepte le ZIP OpenAI, un dossier decompresse, ou conversations.json."""
    if path.is_dir():
        candidate = path / "conversations.json"
        if not candidate.exists():
            found = list(path.rglob("conversations.json"))
            if not found:
                sys.exit(f"Erreur : conversations.json introuvable dans {path}")
            candidate = found[0]
        raw = json.loads(candidate.read_text(encoding="utf-8"))
    elif path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as zf:
            names = [n for n in zf.namelist() if n.endswith("conversations.json")]
            if not names:
                sys.exit(f"Erreur : conversations.json absent de {path.name}")
            raw = json.loads(zf.read(names[0]).decode("utf-8"))
    elif path.suffix.lower() == ".json":
        raw = json.loads(path.read_text(encoding="utf-8"))
    else:
        sys.exit(f"Erreur : format non reconnu ({path.name}). Attendu : .zip, .json ou un dossier.")

    if isinstance(raw, dict):
        raw = raw.get("conversations", [])
    if not isinstance(raw, list):
        sys.exit("Erreur : structure inattendue dans conversations.json")
    return raw


def extract_parts(message: dict) -> str:
    """Rend le contenu d'un message en texte, quel que soit son content_type."""
    content = message.get("content") or {}
    ctype = content.get("content_type")

    if ctype == "text":
        return "\n".join(p for p in content.get("parts", []) if isinstance(p, str))

    if ctype == "multimodal_text":
        chunks = []
        for part in content.get("parts", []):
            if isinstance(part, str):
                chunks.append(part)
            elif isinstance(part, dict):
                pointer = part.get("asset_pointer") or part.get("file_id") or ""
                name = part.get("name") or pointer or "fichier"
                chunks.append(f"[piece jointe : {name}]")
        return "\n".join(c for c in chunks if c)

    if ctype == "code":
        return "```\n" + (content.get("text") or "") + "\n```"

    if ctype == "execution_output":
        return "```\n" + (content.get("text") or "") + "\n```"

    for key in ("text", "result"):
        if isinstance(content.get(key), str):
            return content[key]
    return ""


def is_visible(node_message: dict) -> bool:
    meta = node_message.get("metadata") or {}
    if meta.get("is_visually_hidden_from_conversation"):
        return False
    author = (node_message.get("author") or {}).get("role")
    if author == "system":
        return False
    if author == "tool" and not meta.get("is_user_system_message", False):
        # Sorties d'outils internes : bruit pour une archive de lecture.
        return False
    recipient = node_message.get("recipient")
    if recipient and recipient != "all":
        return False
    return True


def linear_thread(conv: dict) -> list[dict]:
    """
    Remonte de current_node vers la racine via 'parent' puis inverse.
    C'est le seul moyen fiable d'obtenir le fil reellement affiche,
    sans les branches abandonnees apres une regeneration.
    """
    mapping = conv.get("mapping") or {}
    node_id = conv.get("current_node")
    if not node_id:
        # Repli : pas de current_node, on prend tout dans l'ordre chronologique.
        msgs = [n.get("message") for n in mapping.values() if n.get("message")]
        msgs = [m for m in msgs if is_visible(m)]
        return sorted(msgs, key=lambda m: m.get("create_time") or 0)

    chain, seen = [], set()
    while node_id and node_id in mapping and node_id not in seen:
        seen.add(node_id)
        node = mapping[node_id]
        message = node.get("message")
        if message and is_visible(message):
            chain.append(message)
        node_id = node.get("parent")
    chain.reverse()
    return chain


def parse_conversation(conv: dict) -> dict | None:
    conv_id = conv.get("conversation_id") or conv.get("id")
    if not conv_id:
        return None

    messages = []
    for message in linear_thread(conv):
        text = extract_parts(message).strip()
        if not text:
            continue
        messages.append({
            "role": (message.get("author") or {}).get("role", "unknown"),
            "time": ts_to_dt(message.get("create_time")),
            "text": text,
        })

    if not messages:
        return None

    created = ts_to_dt(conv.get("create_time")) or messages[0]["time"]
    updated = ts_to_dt(conv.get("update_time")) or messages[-1]["time"]
    title = (conv.get("title") or "").strip() or "Sans titre"

    return {
        "id": conv_id,
        "title": title,
        "url": CHAT_URL.format(conv_id),
        "created": created,
        "updated": updated,
        "messages": messages,
        "chars": sum(len(m["text"]) for m in messages),
        "project": (conv.get("conversation_origin") or {}).get("title")
                   if isinstance(conv.get("conversation_origin"), dict) else None,
    }


# --------------------------------------------------------------------------
# Classification
# --------------------------------------------------------------------------

class Classifier:
    def __init__(self, taxonomy: dict):
        self.min_score = taxonomy.get("min_score", 4)
        self.title_weight = taxonomy.get("title_weight", 3)
        self.body_weight = taxonomy.get("body_weight", 1)
        self.body_cap = taxonomy.get("body_cap_per_keyword", 4)
        self.max_tags = taxonomy.get("max_tags", 3)
        self.fallback = taxonomy.get("fallback_tag", "Non classe")
        self.categories = {
            name: [normalize(k) for k in keywords]
            for name, keywords in taxonomy.get("categories", {}).items()
        }

    def score(self, title: str, body: str) -> dict[str, int]:
        ntitle, nbody = normalize(title), normalize(body)
        scores = {}
        for name, keywords in self.categories.items():
            total = 0
            for keyword in keywords:
                if keyword in ntitle:
                    total += self.title_weight
                hits = nbody.count(keyword)
                if hits:
                    total += min(hits, self.body_cap) * self.body_weight
            if total:
                scores[name] = total
        return scores

    def tags(self, title: str, body: str) -> tuple[list[str], dict[str, int]]:
        scores = self.score(title, body)
        kept = [n for n, s in sorted(scores.items(), key=lambda kv: -kv[1])
                if s >= self.min_score][:self.max_tags]
        return (kept or [self.fallback]), scores


# --------------------------------------------------------------------------
# Rendu Markdown
# --------------------------------------------------------------------------

def render_markdown(conv: dict, tags: list[str]) -> str:
    created = conv["created"].strftime("%Y-%m-%d %H:%M") if conv["created"] else "inconnue"
    lines = [
        "---",
        f'titre: "{conv["title"].replace(chr(34), chr(39))}"',
        f"date: {created}",
        f"tags: [{', '.join(tags)}]",
        f"source: {conv['url']}",
        f"messages: {len(conv['messages'])}",
        "---",
        "",
        f"# {conv['title']}",
        "",
    ]
    for message in conv["messages"]:
        who = ROLE_LABEL.get(message["role"], message["role"])
        stamp = message["time"].strftime("%d/%m/%Y %H:%M") if message["time"] else ""
        lines.append(f"## {who}" + (f" _{stamp}_" if stamp else ""))
        lines.append("")
        lines.append(message["text"])
        lines.append("")
    return "\n".join(lines)


def markdown_path(conv: dict) -> Path:
    date = conv["created"] or datetime.now(timezone.utc)
    return ARCHIVE_DIR / str(date.year) / f"{date:%Y-%m-%d}-{slugify(conv['title'])}.md"


# --------------------------------------------------------------------------
# Conversion Markdown -> blocs Notion
# --------------------------------------------------------------------------

def rich_text(text: str) -> list[dict]:
    """Decoupe en objets rich_text de 2000 caracteres maximum."""
    text = text or ""
    return [
        {"type": "text", "text": {"content": text[i:i + MAX_RICH_TEXT]}}
        for i in range(0, max(len(text), 1), MAX_RICH_TEXT)
    ] or [{"type": "text", "text": {"content": ""}}]


def text_blocks(text: str, block_type: str = "paragraph", **extra) -> list[dict]:
    """Un bloc par tranche de MAX_SEGMENTS_PER_BLOCK segments rich_text."""
    segments = rich_text(text)
    blocks = []
    for i in range(0, len(segments), MAX_SEGMENTS_PER_BLOCK):
        payload = {"rich_text": segments[i:i + MAX_SEGMENTS_PER_BLOCK]}
        payload.update(extra)
        blocks.append({"object": "block", "type": block_type, block_type: payload})
    return blocks


def markdown_to_blocks(text: str) -> list[dict]:
    """
    Conversion pragmatique. Le formatage inline (gras, liens) est aplati en
    texte brut : on privilegie la robustesse de l'import sur la fidelite typo.
    Les tableaux Markdown sont conserves en bloc de code pour garder l'alignement.
    """
    blocks: list[dict] = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        if line.startswith("```"):
            language = line[3:].strip() or "plain text"
            buffer, i = [], i + 1
            while i < len(lines) and not lines[i].startswith("```"):
                buffer.append(lines[i])
                i += 1
            i += 1
            blocks.extend(text_blocks("\n".join(buffer), "code", language=language[:40]))
            continue

        if line.startswith("|") and line.endswith("|"):
            buffer = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                buffer.append(lines[i].rstrip())
                i += 1
            blocks.extend(text_blocks("\n".join(buffer), "code", language="plain text"))
            continue

        if not line.strip():
            i += 1
            continue

        if re.match(r"^-{3,}$|^\*{3,}$", line.strip()):
            blocks.append({"object": "block", "type": "divider", "divider": {}})
        elif line.startswith("#### "):
            blocks.extend(text_blocks(line[5:], "heading_3"))
        elif line.startswith("### "):
            blocks.extend(text_blocks(line[4:], "heading_3"))
        elif line.startswith("## "):
            blocks.extend(text_blocks(line[3:], "heading_2"))
        elif line.startswith("# "):
            blocks.extend(text_blocks(line[2:], "heading_1"))
        elif line.startswith("> "):
            blocks.extend(text_blocks(line[2:], "quote"))
        elif re.match(r"^\s*[-*+]\s+", line):
            blocks.extend(text_blocks(re.sub(r"^\s*[-*+]\s+", "", line), "bulleted_list_item"))
        elif re.match(r"^\s*\d+[.)]\s+", line):
            blocks.extend(text_blocks(re.sub(r"^\s*\d+[.)]\s+", "", line), "numbered_list_item"))
        else:
            blocks.extend(text_blocks(line, "paragraph"))
        i += 1

    return blocks


def chunk_blocks(blocks: list[dict]) -> list[list[dict]]:
    """
    Decoupe en lots respectant les DEUX limites Notion : 100 blocs par requete
    et 500 Ko de payload. Un seul bloc peut peser 16 Ko, donc 100 blocs
    depassent le poids bien avant de depasser le compte.
    """
    lots: list[list[dict]] = []
    current: list[dict] = []
    weight = 0
    for block in blocks:
        size = len(json.dumps(block, ensure_ascii=False).encode("utf-8"))
        if current and (len(current) >= MAX_BLOCKS_PER_CALL or weight + size > MAX_PAYLOAD_BYTES):
            lots.append(current)
            current, weight = [], 0
        current.append(block)
        weight += size
    if current:
        lots.append(current)
    return lots


def conversation_blocks(conv: dict) -> list[dict]:
    blocks = [{
        "object": "block", "type": "callout",
        "callout": {
            "rich_text": rich_text(
                f"Import depuis l'export officiel OpenAI le "
                f"{datetime.now(timezone.utc):%d/%m/%Y}. "
                f"{len(conv['messages'])} messages, {conv['chars']} caracteres."
            ),
            "icon": {"emoji": "📦"},
        },
    }]
    for message in conv["messages"]:
        who = ROLE_LABEL.get(message["role"], message["role"])
        stamp = message["time"].strftime("%d/%m/%Y %H:%M") if message["time"] else ""
        blocks.extend(text_blocks(f"{who} {stamp}".strip(), "heading_3"))
        blocks.extend(markdown_to_blocks(message["text"]))
    return blocks


# --------------------------------------------------------------------------
# Client Notion throttle
# --------------------------------------------------------------------------

class ThrottledNotion:
    """
    Respecte les deux limites Notion : 3 requetes/seconde en moyenne,
    et 1000 requetes / 5 minutes par workspace (on vise WINDOW_BUDGET).
    """

    def __init__(self, client):
        self.client = client
        self.calls: list[float] = []
        self.total = 0

    def _wait(self):
        now = time.monotonic()
        self.calls = [t for t in self.calls if now - t < 300]
        if len(self.calls) >= WINDOW_BUDGET:
            pause = 300 - (now - self.calls[0]) + 1
            print(f"  [pause {pause:.0f}s : quota 5 minutes atteint]")
            time.sleep(max(pause, 1))
            now = time.monotonic()
            self.calls = [t for t in self.calls if now - t < 300]
        if self.calls:
            delta = now - self.calls[-1]
            if delta < 1 / REQ_PER_SECOND:
                time.sleep(1 / REQ_PER_SECOND - delta)
        self.calls.append(time.monotonic())
        self.total += 1

    def call(self, func, **kwargs):
        for attempt in range(5):
            self._wait()
            try:
                return func(**kwargs)
            except Exception as exc:  # noqa: BLE001 - on inspecte le status
                status = getattr(exc, "status", None)
                if status == 429:
                    delay = float(getattr(exc, "headers", {}).get("Retry-After", 2 ** attempt))
                    print(f"  [429 : attente {delay:.0f}s]")
                    time.sleep(delay)
                    continue
                if status and 500 <= status < 600 and attempt < 4:
                    time.sleep(2 ** attempt)
                    continue
                raise
        raise RuntimeError("Notion : echec apres 5 tentatives")


def conv_id_from_url(url: str | None) -> str | None:
    if not url:
        return None
    match = re.search(r"/c/([0-9a-fA-F-]{8,})", url)
    return match.group(1) if match else None


def fetch_existing(api: ThrottledNotion, db_id: str) -> dict[str, dict]:
    """Index des pages Notion existantes, cle = identifiant de conversation."""
    existing, cursor = {}, None
    while True:
        payload = {"database_id": db_id, "page_size": 100}
        if cursor:
            payload["start_cursor"] = cursor
        result = api.call(api.client.databases.query, **payload)
        for page in result.get("results", []):
            props = page.get("properties", {})
            url = (props.get("URL") or {}).get("url")
            cid = conv_id_from_url(url)
            if not cid:
                continue
            status = ((props.get("SyncStatus") or {}).get("select") or {}).get("name")
            tags = [t["name"] for t in (props.get("Tags") or {}).get("multi_select", [])]
            existing[cid] = {"page_id": page["id"], "status": status, "tags": tags}
        if not result.get("has_more"):
            return existing
        cursor = result.get("next_cursor")


def build_properties(conv: dict, tags: list[str]) -> dict:
    props = {
        "Title": {"title": rich_text(conv["title"])},
        "URL": {"url": conv["url"]},
        "Tags": {"multi_select": [{"name": t} for t in tags]},
        "SyncStatus": {"select": {"name": "Complete"}},
        "ExportVersion": {"rich_text": rich_text(EXPORT_VERSION)},
        "SyncCheckpoint": {"number": len(conv["messages"])},
    }
    if conv["created"]:
        props["ChatTime"] = {"date": {"start": conv["created"].isoformat()}}
    if conv.get("project"):
        props["ProjectName"] = {"rich_text": rich_text(conv["project"])}
    return props


def clear_children(api: ThrottledNotion, page_id: str) -> None:
    """Vide le contenu d'une page avant reecriture (reparation des Partial)."""
    cursor = None
    while True:
        payload = {"block_id": page_id, "page_size": 100}
        if cursor:
            payload["start_cursor"] = cursor
        result = api.call(api.client.blocks.children.list, **payload)
        for block in result.get("results", []):
            api.call(api.client.blocks.delete, block_id=block["id"])
        if not result.get("has_more"):
            return
        cursor = result.get("next_cursor")


def write_page(api: ThrottledNotion, db_id: str, conv: dict, tags: list[str],
               existing: dict | None) -> str:
    lots = chunk_blocks(conversation_blocks(conv))
    head, tail = (lots[0] if lots else []), lots[1:]
    props = build_properties(conv, tags)

    if existing:
        page_id = existing["page_id"]
        clear_children(api, page_id)
        api.call(api.client.pages.update, page_id=page_id, properties=props)
        if head:
            api.call(api.client.blocks.children.append, block_id=page_id, children=head)
    else:
        page = api.call(
            api.client.pages.create,
            parent={"database_id": db_id},
            properties=props,
            children=head,
        )
        page_id = page["id"]

    for lot in tail:
        api.call(api.client.blocks.children.append, block_id=page_id, children=lot)
    return page_id


# --------------------------------------------------------------------------
# Rapport
# --------------------------------------------------------------------------

def write_report(stats: dict, per_tag: Counter, unclassified: list[str],
                 actions: Counter) -> None:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Rapport d'import ChatGPT",
        "",
        f"Genere le {datetime.now(timezone.utc):%d/%m/%Y %H:%M} UTC.",
        "",
        "## Volume",
        "",
        f"- Conversations dans l'export : **{stats['total']}**",
        f"- Retenues (non vides) : **{stats['kept']}**",
        f"- Ignorees (vides) : {stats['empty']}",
        f"- Periode : {stats['first']} -> {stats['last']}",
        f"- Volume texte : {stats['chars'] // 1000} k caracteres",
        "",
        "## Classification",
        "",
        "| Tag | Conversations |",
        "|---|---|",
    ]
    for tag, count in per_tag.most_common():
        lines.append(f"| {tag} | {count} |")
    lines += [
        "",
        "## Actions Notion",
        "",
        "| Action | Nombre |",
        "|---|---|",
    ]
    for action, count in actions.most_common():
        lines.append(f"| {action} | {count} |")

    if unclassified:
        lines += ["", f"## Non classees ({len(unclassified)})", "",
                  "A relire pour enrichir `chatgpt-taxonomy.json` :", ""]
        lines += [f"- {t}" for t in unclassified[:80]]
        if len(unclassified) > 80:
            lines.append(f"- ... et {len(unclassified) - 80} autres")

    REPORT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------
# Programme principal
# --------------------------------------------------------------------------

def notion_database_id() -> str:
    config = load_json(CONFIG_FILE)
    for source in config.get("sources", []):
        if source.get("type") == "chatgpt_archives":
            return source["id"]
    sys.exit("Erreur : source 'chatgpt_archives' absente de notion-config.json")


def connect_notion() -> ThrottledNotion:
    try:
        from dotenv import load_dotenv
        from notion_client import Client
    except ImportError:
        sys.exit("Dependances manquantes. Lancer : pip install notion-client python-dotenv")
    load_dotenv(ROOT / ".env")
    token = os.getenv("NOTION_TOKEN")
    if not token:
        sys.exit("Erreur : NOTION_TOKEN manquant. Creer .env avec NOTION_TOKEN=ntn_xxxx")
    return ThrottledNotion(Client(auth=token))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Archive les conversations ChatGPT vers Markdown local et Notion.")
    parser.add_argument("--export", required=True,
                        help="ZIP OpenAI, dossier decompresse, ou conversations.json")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true",
                      help="Analyse et rapport, aucune ecriture")
    mode.add_argument("--local", action="store_true",
                      help="Ecrit les Markdown locaux uniquement")
    mode.add_argument("--push", action="store_true",
                      help="Markdown local + creation/reparation des pages Notion")
    mode.add_argument("--tags-only", action="store_true",
                      help="Met a jour les tags des pages Notion existantes, contenu intact")
    parser.add_argument("--limit", type=int,
                        help="Ne traiter que les N conversations les plus recentes")
    parser.add_argument("--since", help="Ne traiter qu'a partir de cette date (AAAA-MM-JJ)")
    parser.add_argument("--force", action="store_true",
                        help="Reecrit meme les conversations deja marquees Complete")
    args = parser.parse_args()

    taxonomy = load_json(TAXONOMY_FILE)
    classifier = Classifier(taxonomy)

    raw = read_export(Path(args.export).expanduser())
    print(f"Export lu : {len(raw)} conversations brutes.")

    conversations, empty = [], 0
    for item in raw:
        parsed = parse_conversation(item)
        if parsed:
            conversations.append(parsed)
        else:
            empty += 1

    conversations.sort(key=lambda c: c["created"] or datetime.min.replace(tzinfo=timezone.utc),
                       reverse=True)

    if args.since:
        cutoff = datetime.strptime(args.since, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        conversations = [c for c in conversations if c["created"] and c["created"] >= cutoff]
    if args.limit:
        conversations = conversations[:args.limit]

    if not conversations:
        sys.exit("Aucune conversation a traiter apres filtrage.")

    dates = [c["created"] for c in conversations if c["created"]]
    stats = {
        "total": len(raw),
        "kept": len(conversations),
        "empty": empty,
        "chars": sum(c["chars"] for c in conversations),
        "first": f"{min(dates):%d/%m/%Y}" if dates else "?",
        "last": f"{max(dates):%d/%m/%Y}" if dates else "?",
    }

    # Classification
    per_tag, unclassified = Counter(), []
    for conv in conversations:
        body = "\n".join(m["text"] for m in conv["messages"])
        conv["tags"], _ = classifier.tags(conv["title"], body)
        per_tag.update(conv["tags"])
        if conv["tags"] == [classifier.fallback]:
            unclassified.append(conv["title"])

    actions = Counter()

    # Markdown local
    if args.local or args.push:
        for conv in conversations:
            path = markdown_path(conv)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(render_markdown(conv, conv["tags"]), encoding="utf-8")
            actions["markdown ecrit"] += 1
        print(f"Markdown : {actions['markdown ecrit']} fichiers dans {ARCHIVE_DIR.relative_to(ROOT)}/")

    # Notion
    if args.push or args.tags_only:
        api = connect_notion()
        db_id = notion_database_id()
        print("Lecture de la base Notion existante...")
        existing = fetch_existing(api, db_id)
        print(f"  {len(existing)} pages deja presentes.")

        for index, conv in enumerate(conversations, 1):
            known = existing.get(conv["id"])
            label = conv["title"][:50]

            if args.tags_only:
                if not known:
                    actions["absente de Notion (ignoree)"] += 1
                    continue
                if known["tags"] and not args.force:
                    actions["tags deja presents"] += 1
                    continue
                api.call(api.client.pages.update, page_id=known["page_id"],
                         properties={"Tags": {"multi_select":
                                              [{"name": t} for t in conv["tags"]]}})
                actions["tags mis a jour"] += 1
            else:
                if known and known["status"] == "Complete" and not args.force:
                    actions["deja complete (ignoree)"] += 1
                    continue
                write_page(api, db_id, conv, conv["tags"], known)
                actions["reparee" if known else "creee"] += 1

            if index % 25 == 0:
                print(f"  {index}/{len(conversations)} ... {label}")

        print(f"Notion : {api.total} requetes emises.")

    write_report(stats, per_tag, unclassified, actions)

    print("\n--- Resume ---")
    print(f"Conversations retenues : {stats['kept']} ({stats['first']} -> {stats['last']})")
    for tag, count in per_tag.most_common():
        print(f"  {tag:<14} {count}")
    for action, count in actions.most_common():
        print(f"  {action:<28} {count}")
    print(f"Rapport : {REPORT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
