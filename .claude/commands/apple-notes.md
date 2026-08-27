# Commande /apple-notes

> Migre les notes Apple exportées de Njaho vers Notion.

## Ce que tu dois faire

### Étape 1 : Vérifier l'export

Regarde le dossier `context/import/apple-notes/`.

- S'il est vide ou ne contient que le README, arrête-toi et explique à Njaho comment exporter ses notes (les trois options sont détaillées dans `context/import/apple-notes/README.md`). Ne devine pas, ne fabrique pas de contenu.
- S'il contient des fichiers `.md`, `.markdown` ou `.txt`, continue.

### Étape 2 : Vérifier la configuration

Lis le bloc `apple_notes` de `notion-config.json` :

- `target.id` doit être renseigné (pas de `REMPLACER_...`). Sinon, demande à Njaho l'ID de la base Notion cible, ou propose de créer la base via les outils MCP Notion avec les propriétés `Dossier` (select), `Source` (multi-select), `Chemin` (texte), `Date` (date).
- Vérifie que `NOTION_TOKEN` existe dans `.env`. Sinon, signale-le sans jamais afficher la valeur du jeton.

### Étape 3 : Simulation obligatoire

Lance toujours la simulation avant d'écrire quoi que ce soit :

```bash
python3 scripts/apple-notes-to-notion.py --dry-run
```

Présente à Njaho : le nombre de notes, les titres détectés, les notes déjà migrées, les pièces jointes locales non migrables. Attends sa validation.

### Étape 4 : Migration

Après validation :

```bash
python3 scripts/apple-notes-to-notion.py
```

Si Njaho hésite ou si l'export est volumineux (plus de 50 notes), propose d'abord `--limit 5` pour vérifier le rendu dans Notion avant de tout pousser.

### Étape 5 : Rapport

```
Migration Apple Notes vers Notion terminée.

Notes lues : [nombre]
Pages créées : [nombre]
Pages mises à jour : [nombre]
Notes inchangées ignorées : [nombre]

Pièces jointes à réimporter à la main : [nombre]
Echecs : [liste si présents]
```

Si des notes contiennent des informations importantes sur les projets, objectifs ou activités de Njaho, signale-le et propose une mise à jour de `context/CONTEXT.md`, conformément à la règle de maintien du contexte dans CLAUDE.md.

---

## Règles

- Jamais de migration sans simulation validée au préalable
- Ne jamais dupliquer une note déjà migrée : le fichier d'état `apple-notes-sync-state.json` fait foi, ne pas le supprimer
- Ne jamais modifier ni supprimer les fichiers d'export tant que Njaho n'a pas confirmé que le résultat dans Notion lui convient
- En cas d'échec de l'API Notion (jeton invalide, base non partagée avec l'intégration), expliquer la cause exacte plutôt que de réessayer en boucle
- Ajouter une entrée dans HISTORY.md après une migration réussie (le script s'en charge automatiquement)
