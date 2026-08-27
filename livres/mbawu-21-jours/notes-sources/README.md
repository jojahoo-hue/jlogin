# Notes sources — Nza Ngai dia Nzayi / Mbawu

> Déposer ici toute la matière brute qui alimentera le livre.
> Ce dossier est la seule source autorisée pour la rédaction.

---

## Ce qu'il faut déposer

Tout ce qui touche à Mbawu et aux vingt-et-un jours, dans le projet Nza Ngai dia Nzayi :

- Conversations et échanges du projet (exports ChatGPT ou Notion)
- Notes de séances, d'initiations, de formations
- Transcriptions Plaud liées au sujet
- Journal des vingt-et-un jours, jour par jour, s'il existe
- Schémas, tableaux, correspondances, calendriers
- Sources externes citées (références, auteurs, traditions comparées)

Nommer les fichiers clairement, par exemple :
`notion-mbawu-conversations.md`, `journal-jours-01-07.md`, `plaud-2026-05-12-seance.md`.

---

## Les trois voies d'import

### Option A — Sync Notion depuis le Mac (recommandée)

`api.notion.com` est bloqué dans le cloud Claude Code. La sync doit tourner en local.

1. Récupérer l'ID de la page ou base Notion du projet Nza Ngai dia Nzayi.
   Dans l'URL Notion, c'est la suite de 32 caractères après le titre.
2. Ajouter la source dans `notion-config.json` à la racine du dépôt. Une entrée
   `nza_ngai_mbawu` est déjà préparée, il suffit de remplacer l'ID.
3. Vérifier que la page est bien partagée avec l'intégration Notion.
4. Sur le Mac, à la racine du dépôt :

```bash
pip install notion-client python-dotenv   # une seule fois
echo "NOTION_TOKEN=secret_xxxx" > .env    # une seule fois, .env est gitignoré
python3 scripts/sync-notion.py
git add livres/ context/ notion-config.json
git commit -m "notes: import Notion Nza Ngai dia Nzayi / Mbawu"
git push -u origin claude/mbawu-notes-book-writing-snh51r
```

Le script écrit dans `livres/mbawu-21-jours/notes-sources/notion-nza-ngai-mbawu.md`.

### Option B — Export Notion manuel

Dans Notion, sur la page du projet : `...` en haut à droite → **Exporter** →
format **Markdown & CSV** → inclure les sous-pages. Dézipper le résultat dans ce dossier,
puis commiter et pousser.

C'est l'option la plus simple si le token Notion n'est plus valide. Elle a l'avantage de
récupérer aussi les sous-pages, ce que le script ne fait pas.

### Option C — Copier-coller

Coller le contenu directement dans la conversation avec Claude. Il crée les fichiers ici
et les classe. Adapté si le volume est modeste, quelques milliers de mots.

---

## Note sur le secret initiatique

Ce dossier est versionné dans un dépôt Git. Avant de déposer des notes, trier ce qui peut
y figurer. Ce qui ne doit pas sortir du cercle n'a rien à faire ici, même dans un dépôt
privé. Le périmètre de non-divulgation se décide en Phase 1 du cadrage et se consigne
dans `PLAN.md`.
