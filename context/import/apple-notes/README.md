# Export Apple Notes

> Dépose ici l'export de tes notes Apple, puis lance `/apple-notes` ou le script de migration.

## 1. Exporter depuis Apple Notes

Apple Notes n'exporte pas nativement en Markdown. Trois options, de la plus simple à la plus fidèle.

### Option A : Exporter Notes (le plus simple, recommandé)

L'app **Exporter** (Mac App Store, gratuite pour l'export Markdown) sort un dossier de fichiers `.md` en respectant l'arborescence des dossiers Apple Notes.

1. Ouvrir Exporter, choisir le format **Markdown**
2. Cocher "Preserve folder structure"
3. Exporter vers `context/import/apple-notes/`

### Option B : Script AppleScript (aucune app tierce)

Coller ce script dans **Éditeur de script** sur le Mac, puis l'exécuter. Il écrit un `.md` par note dans le dossier d'export.

```applescript
set destination to (path to home folder as text) & "apple-notes-export:"
do shell script "mkdir -p " & quoted form of POSIX path of destination
tell application "Notes"
  repeat with theNote in notes
    set noteName to name of theNote
    set noteBody to plaintext of theNote
    set safeName to do shell script "echo " & quoted form of noteName & " | tr '/:' '--' | cut -c1-80"
    set filePath to POSIX path of destination & safeName & ".md"
    do shell script "cat > " & quoted form of filePath & " <<'EOF'
" & noteBody & "
EOF"
  end repeat
end tell
```

Puis copier le dossier `~/apple-notes-export/` dans `context/import/apple-notes/`.

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

## 3. Migrer vers Notion

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

## 4. Après la migration

Une fois les notes dans Notion et vérifiées, ce dossier peut être vidé. Garde `apple-notes-sync-state.json` si tu comptes refaire des exports Apple Notes plus tard.
