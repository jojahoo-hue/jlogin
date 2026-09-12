# Commande /archive-chatgpt

> Archive l'intégralité des conversations ChatGPT vers Markdown local et la base Notion.

## Pourquoi cette commande

L'extension navigateur "Save ChatGPT to Notion" capture le DOM de la page. Elle
tronque les longues conversations (statut `Partial`), découpe en `Part 1/3`, échoue
sur les pièces jointes (erreur 403) et ne synchronise que les 28 dernières
conversations. Elle reste utile au fil de l'eau, mais elle ne peut pas servir de
socle d'archivage.

L'export officiel OpenAI est le seul export exhaustif. Cette commande le traite.

## Prérequis

1. Dans ChatGPT : **Réglages > Contrôle des données > Exporter les données**.
   Le lien de téléchargement arrive par mail en quelques heures.
2. `pip install notion-client python-dotenv`
3. Un fichier `.env` à la racine avec `NOTION_TOKEN=ntn_xxxx`
   (intégration Notion créée sur notion.so/my-integrations, partagée avec la base
   `ChatGPT conversations`).

## Déroulé

### Étape 1 : analyser avant d'écrire

```bash
python3 scripts/archive-chatgpt.py --export ~/Downloads/export.zip --dry-run
```

Produit `context/import/chatgpt-archives/_rapport-import.md` : volume, période,
répartition par tag, et la liste des conversations non classées.

Lire le rapport et vérifier la répartition. Si trop de conversations tombent en
`Non classe`, enrichir `chatgpt-taxonomy.json` puis relancer. Aucune écriture n'a
lieu à cette étape.

### Étape 2 : écrire les Markdown locaux

```bash
python3 scripts/archive-chatgpt.py --export ~/Downloads/export.zip --local
```

Un fichier par conversation dans `context/import/chatgpt-archives/AAAA/`, avec
en-tête YAML (titre, date, tags, URL source). Ce dossier est volontairement dans
`.gitignore` : le dépôt `jlogin` est **public**.

### Étape 3 : pousser vers Notion

```bash
python3 scripts/archive-chatgpt.py --export ~/Downloads/export.zip --push
```

Déduplique via l'URL `chatgpt.com/c/<id>` déjà présente sur les pages existantes.
Crée ce qui manque, répare les `Partial` et `In progress`, ignore les `Complete`.
Ajouter `--force` pour tout réécrire.

### Étape 4 : classer l'existant sans toucher au contenu

```bash
python3 scripts/archive-chatgpt.py --export ~/Downloads/export.zip --tags-only
```

Ne met à jour que la propriété `Tags` des pages déjà dans Notion.

## Options utiles

| Option | Effet |
|---|---|
| `--since 2026-01-01` | Ne traite que les conversations à partir de cette date |
| `--limit 50` | Ne traite que les N plus récentes, pour un essai |
| `--force` | Réécrit même les conversations déjà `Complete` |

Commencer par `--limit 20 --push` pour valider le rendu dans Notion avant de
lancer la totalité.

## Taxonomie

`chatgpt-taxonomy.json` à la racine. Huit catégories : Supervision, Exploitation,
Contrats, Formation, Artistique, Recherche, Crypto, Perso.

Les mots-clés sont cherchés en minuscules sans accents, avec un poids fort sur le
titre et faible sur le corps. `min_score` règle le seuil, `max_tags` le nombre de
tags par conversation. Ajuster ce fichier ne demande aucune modification du code.

## Règles

- Ne jamais committer `context/import/chatgpt-archives/` ni le ZIP d'export :
  le dépôt est public et les conversations contiennent des audits, des devis et
  des données personnelles.
- Toujours lancer `--dry-run` avant `--push`.
- Après un import réussi, ajouter une entrée dans `context/HISTORY.md`.
- Le script respecte les limites de l'API Notion (3 requêtes/seconde, 1000 par
  tranche de 5 minutes). Sur environ 1 800 conversations, prévoir plusieurs heures
  et laisser le script gérer ses pauses.
