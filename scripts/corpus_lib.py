#!/usr/bin/env python3
"""
Bibliothèque commune du corpus Njaho.

Fournit :
  - un client Notion minimal (stdlib uniquement, pas de dépendance externe)
  - le chargement de la taxonomie contrôlée (corpus/taxonomie.yaml)
  - l'inférence de thème à partir du titre, des sujets libres et du résumé
  - les utilitaires de nommage de fichiers

Requiert la variable d'environnement NOTION_TOKEN (fichier .env à la racine).
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "corpus"
FICHES = CORPUS / "fiches"
TAXONOMIE = CORPUS / "taxonomie.yaml"
INDEX_JSON = CORPUS / "index.json"

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

# Bases Notion de Njaho
DB_PLAUD_ARCHIVE = "36f92f894f8c81b79bc5dbec08bf24d4"
DB_MANUSCRITS = "36f92f894f8c810ab451f42c4b319cd7"


# --------------------------------------------------------------------------
# Environnement
# --------------------------------------------------------------------------

def load_env() -> None:
    """Charge le .env à la racine, sans dépendance à python-dotenv."""
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def get_token() -> str:
    load_env()
    token = os.getenv("NOTION_TOKEN")
    if not token:
        sys.exit(
            "Erreur : NOTION_TOKEN absent.\n"
            "Crée un fichier .env à la racine du projet avec :\n"
            "  NOTION_TOKEN=ntn_xxxxxxxx\n"
            "Le token s'obtient sur https://www.notion.so/my-integrations "
            "et l'intégration doit être connectée aux bases Plaud Archive et Manuscrits."
        )
    return token


# --------------------------------------------------------------------------
# Client Notion minimal
# --------------------------------------------------------------------------

class Notion:
    def __init__(self, token: str | None = None, verbose: bool = True):
        self.token = token or get_token()
        self.verbose = verbose
        self.calls = 0

    def _request(self, method: str, path: str, payload: dict | None = None) -> dict:
        url = f"{NOTION_API}{path}"
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Bearer {self.token}")
        req.add_header("Notion-Version", NOTION_VERSION)
        req.add_header("Content-Type", "application/json")

        for attempt in range(6):
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    self.calls += 1
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", "replace")
                # 429 : rate limit. 502/503/504 : hoquet côté Notion.
                if exc.code in (429, 500, 502, 503, 504) and attempt < 5:
                    wait = float(exc.headers.get("Retry-After", 0) or (2 ** attempt))
                    if self.verbose:
                        print(f"  … {exc.code}, nouvelle tentative dans {wait:.0f}s")
                    time.sleep(wait)
                    continue
                raise RuntimeError(f"Notion {method} {path} -> {exc.code}\n{body}") from exc
            except urllib.error.URLError as exc:
                if attempt < 5:
                    time.sleep(2 ** attempt)
                    continue
                raise RuntimeError(f"Réseau indisponible : {exc}") from exc
        raise RuntimeError("Échec après 6 tentatives")

    # -- lecture ----------------------------------------------------------

    def query_database(self, database_id: str, page_size: int = 100):
        """Itère sur toutes les lignes d'une base, en gérant la pagination."""
        cursor = None
        while True:
            payload = {"page_size": page_size}
            if cursor:
                payload["start_cursor"] = cursor
            res = self._request("POST", f"/databases/{database_id}/query", payload)
            for row in res.get("results", []):
                yield row
            if not res.get("has_more"):
                return
            cursor = res.get("next_cursor")

    def get_database(self, database_id: str) -> dict:
        return self._request("GET", f"/databases/{database_id}")

    def block_children(self, block_id: str):
        cursor = None
        while True:
            path = f"/blocks/{block_id}/children?page_size=100"
            if cursor:
                path += f"&start_cursor={cursor}"
            res = self._request("GET", path)
            for block in res.get("results", []):
                yield block
            if not res.get("has_more"):
                return
            cursor = res.get("next_cursor")

    # -- écriture ---------------------------------------------------------

    def update_page(self, page_id: str, properties: dict) -> dict:
        return self._request("PATCH", f"/pages/{page_id}", {"properties": properties})

    def archive_page(self, page_id: str) -> dict:
        return self._request("PATCH", f"/pages/{page_id}", {"archived": True})

    def update_database(self, database_id: str, properties: dict) -> dict:
        return self._request("PATCH", f"/databases/{database_id}", {"properties": properties})

    def create_page(self, database_id: str, properties: dict, children: list | None = None) -> dict:
        payload = {"parent": {"database_id": database_id}, "properties": properties}
        if children:
            payload["children"] = children
        return self._request("POST", "/pages", payload)

    def append_blocks(self, page_id: str, children: list) -> dict:
        return self._request("PATCH", f"/blocks/{page_id}/children", {"children": children})


# --------------------------------------------------------------------------
# Propriétés Notion -> valeurs Python
# --------------------------------------------------------------------------

def plain(prop: dict | None) -> str:
    """Aplatit une propriété Notion en texte."""
    if not prop:
        return ""
    kind = prop.get("type")
    if kind in ("title", "rich_text"):
        return "".join(t.get("plain_text", "") for t in prop.get(kind, []))
    if kind == "select":
        sel = prop.get("select")
        return sel.get("name", "") if sel else ""
    if kind == "multi_select":
        return ", ".join(o.get("name", "") for o in prop.get("multi_select", []))
    if kind == "date":
        date = prop.get("date")
        return (date or {}).get("start", "") or ""
    if kind == "number":
        val = prop.get("number")
        return "" if val is None else str(val)
    if kind == "checkbox":
        return "oui" if prop.get("checkbox") else "non"
    if kind == "url":
        return prop.get("url") or ""
    return ""


def multi_list(prop: dict | None) -> list[str]:
    if not prop or prop.get("type") != "multi_select":
        return []
    return [o.get("name", "") for o in prop.get("multi_select", []) if o.get("name")]


BLOCK_PREFIX = {
    "heading_1": "# ",
    "heading_2": "## ",
    "heading_3": "### ",
    "bulleted_list_item": "- ",
    "numbered_list_item": "1. ",
    "quote": "> ",
    "to_do": "- [ ] ",
    "callout": "> ",
}


def blocks_to_markdown(blocks) -> str:
    """Convertit des blocs Notion en markdown simple."""
    lines: list[str] = []
    for block in blocks:
        kind = block.get("type")
        payload = block.get(kind, {})
        rich = payload.get("rich_text")
        if rich is None:
            if kind == "divider":
                lines.append("---")
            continue
        text = "".join(t.get("plain_text", "") for t in rich).rstrip()
        if not text:
            continue
        if kind == "code":
            lang = payload.get("language", "")
            lines.append(f"```{lang}\n{text}\n```")
        else:
            lines.append(BLOCK_PREFIX.get(kind, "") + text)
    return "\n\n".join(lines)


# --------------------------------------------------------------------------
# Taxonomie
# --------------------------------------------------------------------------

def load_taxonomie() -> dict:
    try:
        import yaml  # type: ignore
    except ImportError:
        sys.exit("Dépendance manquante : pip3 install pyyaml")
    if not TAXONOMIE.exists():
        sys.exit(f"Taxonomie introuvable : {TAXONOMIE}")
    return yaml.safe_load(TAXONOMIE.read_text(encoding="utf-8"))


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def build_matcher(taxo: dict) -> list[tuple[str, str, str, list]]:
    """Prépare (id, label, livre, [motifs compilés]) pour chaque thème.

    Les motifs sont appariés sur mot entier, pas en sous-chaîne : sans cela
    l'alias "RIK" se déclenche sur "ateliers", et "art" sur "carte".
    """
    out = []
    for theme in taxo.get("themes", []):
        vus, motifs = set(), []
        for brut in [theme["label"]] + list(theme.get("alias", [])):
            m = _norm(brut)
            if len(m) < 3 or m in vus:
                continue
            vus.add(m)
            motifs.append(re.compile(r"(?<![a-z0-9])" + re.escape(m) + r"(?![a-z0-9])"))
        out.append((theme["id"], theme["label"], theme.get("livre", ""), motifs))
    return out


# Poids des champs : le titre est bien plus discriminant que le résumé.
POIDS = {"titre": 4, "sujets": 2, "resume": 1}
SCORE_MINIMUM = 2


def infer_themes(matcher, titre: str = "", sujets: str = "", resume: str = "",
                 limite: int = 3) -> list[str]:
    """Retourne les thèmes les plus probables, du plus au moins sûr.

    Le dossier n'entre volontairement pas dans le calcul : "Formations & Ateliers"
    contient "atelier", ce qui contaminait la moitié du corpus.
    """
    champs = {
        "titre": _norm(titre),
        "sujets": _norm(sujets),
        "resume": _norm(resume),
    }
    scores: list[tuple[int, str]] = []
    for _tid, label, _livre, motifs in matcher:
        score = 0
        for champ, poids in POIDS.items():
            texte = champs[champ]
            if not texte:
                continue
            touches = sum(1 for m in motifs if m.search(texte))
            score += poids * min(touches, 3)
        if score >= SCORE_MINIMUM:
            scores.append((score, label))
    scores.sort(key=lambda x: (-x[0], x[1]))
    return [label for _s, label in scores[:limite]]


def theme_to_livre(taxo: dict) -> dict[str, str]:
    return {t["label"]: t.get("livre", "") for t in taxo.get("themes", [])}


# --------------------------------------------------------------------------
# Nommage
# --------------------------------------------------------------------------

def slug(text: str, maxlen: int = 60) -> str:
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    return text[:maxlen].strip("-") or "sans-titre"


def fiche_path(date: str, dossier: str, titre: str) -> Path:
    jour = (date or "0000-00-00")[:10]
    return FICHES / f"{jour}_{slug(dossier, 30)}_{slug(titre)}.md"


def write_if_changed(path: Path, content: str) -> bool:
    """Écrit seulement si le contenu diffère. Retourne True si écrit."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True
