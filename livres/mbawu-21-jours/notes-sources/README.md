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
```

Le script écrit dans `livres/mbawu-21-jours/notes-sources/notion-nza-ngai-mbawu.md`.

Ce fichier est ignoré par Git tant que le dépôt est public, donc il ne part pas sur
GitHub. Il reste lisible en local par Claude Code lancé depuis le Mac. Pour travailler
dessus depuis une session cloud, il faut d'abord passer le dépôt en privé, puis retirer
les deux lignes correspondantes du `.gitignore`.

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

**Le dépôt `jojahoo-hue/jlogin` est public.** Vérifié le 2026-09-03. Tout ce qui y est
commité devient lisible par n'importe qui, indexable, forkable, et reste récupérable dans
l'historique Git même après suppression.

Ce dossier est donc exclu de Git : `.gitignore` bloque `livres/*/notes-sources/**`, seul
ce README est versionné. Les notes que tu déposes ici restent sur ta machine.

Deux conséquences pratiques :

1. **Passe le dépôt en privé** avant d'envisager de versionner quoi que ce soit de la
   matière. GitHub, page du dépôt, Settings, tout en bas, Change repository visibility.
   Tant que ce n'est pas fait, ne retire pas les lignes du `.gitignore`
2. **Une session Claude Code cloud est éphémère.** Des notes non commitées disparaissent
   quand le conteneur est recyclé. Tant que le dépôt est public, garde donc l'original de
   tes notes chez toi, sur le Mac ou dans Notion, et considère ce dossier comme un cache
   de travail, pas comme un lieu de conservation

Le périmètre de ce qui ne s'écrit pas est défini en section 2 de `PLAN.md`.
