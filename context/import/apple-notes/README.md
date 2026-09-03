# Export Apple Notes

> Dépose ici l'export de tes notes Apple, puis lance `/apple-notes` ou le script de migration.

## 1. Exporter depuis Apple Notes

Apple Notes n'exporte pas nativement en Markdown. Trois options, de la plus simple à la plus fidèle.

### Option A : Exporter Notes (le plus simple, recommandé)

L'app **Exporter** (Mac App Store, gratuite pour l'export Markdown) sort un dossier de fichiers `.md` en respectant l'arborescence des dossiers Apple Notes.

1. Ouvrir Exporter, choisir le format **Markdown**
2. Cocher "Preserve folder structure"
3. Exporter vers `context/import/apple-notes/`

### Option B : Le script fourni (aucune app tierce)

Le dépôt contient `scripts/export-apple-notes.applescript`. Sur le Mac, dans le Terminal, à la racine du workspace :

```bash
osascript scripts/export-apple-notes.applescript ~/Documents/jlogin/context/import/apple-notes
```

Adapter le chemin à l'emplacement réel du workspace. Le chemin doit être absolu : `osascript` ignore le dossier courant du Terminal.

Le script écrit un fichier `.md` par note, un sous-dossier par dossier Apple Notes, en UTF-8 (accents et emojis préservés). Il ignore la corbeille, gère les titres en doublon et n'interrompt pas l'export si une note est illisible. Il affiche à la fin le nombre de notes exportées et ignorées.

Au premier lancement, macOS demande l'autorisation de piloter Notes. En cas d'erreur `-1743`, autoriser le Terminal dans Réglages Système → Confidentialité et sécurité → Automatisation → Notes.

### Option C : Copier-coller

Pour quelques notes seulement : créer un fichier `.md` par note, la première ligne servant de titre.

## 2. Format attendu

Un fichier par note, extension `.md`, `.markdown` ou `.txt`. Les sous-dossiers deviennent la propriété `Dossier` dans Notion.

```
context/import/apple-notes/
├── Travail/
│   ├── Reunion NOC 3 mai.md
│   └── Procedure astreinte.md
├── Art/
│   └── Serie Congo geometrique.md
└── Idees.md
```

Le titre de la note est pris, dans cet ordre : le champ `title` du front-matter s'il existe, sinon le premier titre Markdown (`# ...`), sinon la première ligne du fichier (convention Apple Notes), sinon le nom du fichier.

Ce qui est converti en blocs Notion : titres, listes à puces et numérotées, cases à cocher (`- [ ]` et `☐` / `☑`), citations, blocs de code, tableaux, séparateurs, gras / italique / barré / code inline, liens, images distantes.

Les listes imbriquées sont conservées sur trois niveaux, ce qui est le maximum accepté par l'API Notion. Au-delà, les éléments plus profonds sont rattachés au troisième niveau plutôt que perdus.

Les pièces jointes locales (photos, PDF, croquis) ne peuvent pas être poussées par l'API : elles sont signalées dans la page Notion par un encadré avec leur chemin, à réimporter à la main si besoin.

## 3. Préparer la base Notion cible

### Le plus simple : laisser le script la créer

```bash
# Voir la structure qui sera créée
python3 scripts/create-notion-database.py --dry-run

# Créer la base dans une page Notion existante
python3 scripts/create-notion-database.py --parent-page <ID_DE_LA_PAGE>
```

L'ID de page se lit dans son URL Notion : `notion.so/Mes-notes-2d892f894f8c81f789f8e1fcfcb851cd` donne `2d892f894f8c81f789f8e1fcfcb851cd`. Cette page doit d'abord être partagée avec l'intégration (menu `...` de la page → Connexions → choisir l'intégration).

Le script crée la base et inscrit son identifiant dans `notion-config.json`. Rien à recopier à la main.

### En manuel, si tu préfères cliquer

Créer une base de données Notion avec exactement ces propriétés :

| Propriété | Type | Contenu |
|-----------|------|---------|
| `Nom` | Titre | Titre de la note |
| `Dossier` | Sélection | Dossier Apple Notes d'origine |
| `Source` | Sélection multiple | Toujours « Apple Notes » |
| `Chemin` | Texte | Chemin du fichier d'origine |
| `Date` | Date | Date de modification |

Puis partager la base avec l'intégration Notion, copier son ID depuis l'URL, et le coller dans `notion-config.json` → `apple_notes.target.id`.

Les noms de propriétés se changent librement dans `notion-config.json` (bloc `properties` et `title_property`), le script s'y adapte. Une propriété absente de la base est simplement ignorée à la migration, elle ne provoque pas d'erreur.

## 4. Migrer vers Notion

```bash
# Vérifier ce qui sera migré, sans rien écrire
python3 scripts/apple-notes-to-notion.py --dry-run

# Migrer pour de vrai
python3 scripts/apple-notes-to-notion.py

# Tester sur les 5 premières notes seulement
python3 scripts/apple-notes-to-notion.py --limit 5
```

Prérequis : `NOTION_TOKEN` dans `.env`, la base cible renseignée dans `notion-config.json` (`apple_notes.target.id`), et l'intégration Notion partagée avec cette base.

La migration est rejouable sans risque : chaque note migrée est tracée dans `apple-notes-sync-state.json`. Une note inchangée est ignorée, une note modifiée est mise à jour en place, jamais dupliquée.

## 5. Après la migration

Une fois les notes dans Notion et vérifiées, ce dossier peut être vidé. Garde `apple-notes-sync-state.json` si tu comptes refaire des exports Apple Notes plus tard.
