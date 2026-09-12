# Archivage Notes Apple → Notion

Pipeline pour archiver les notes de Notes.app, photos comprises, dans une base de données
Notion. Tourne sur le Mac, en une passe manuelle ou en cron toutes les 6 heures.

## Comment ça marche

```
Notes.app ──AppleScript──> dossier de travail ──Python──> Notion
            (texte + pièces jointes)          (blocs + upload fichiers)
```

| Fichier | Rôle |
|---------|------|
| `apple-notes-export.applescript` | Lit Notes.app, écrit le corps HTML et sauvegarde les pièces jointes |
| `apple-notes-to-notion.py` | Convertit le HTML en blocs Notion, envoie les photos, crée ou met à jour les pages |
| `apple-notes-sync.sh` | Wrapper cron avec log et alerte Telegram en cas d'échec |

L'état est conservé dans `.apple-notes-state.json` à la racine (non versionné) : il retient
pour chaque note son id Apple, la page Notion correspondante et sa date de modification.
Une note déjà archivée et inchangée n'est pas retouchée.

## Installation

### 1. Dépendances

```bash
pip3 install requests python-dotenv
```

### 2. Intégration Notion

1. Créer une intégration interne sur https://www.notion.so/my-integrations
2. Copier le token dans `.env` : `NOTION_TOKEN=ntn_...`
3. Créer une page Notion qui hébergera la base, puis la partager avec l'intégration
   (menu `...` > Connexions > ton intégration)
4. Récupérer l'id de cette page dans son URL et le mettre dans `.env` :
   `NOTION_NOTES_PARENT_PAGE_ID=...`

### 3. Créer la base

```bash
python3 scripts/apple-notes-to-notion.py --create-db
```

Copier l'id affiché dans `.env` sous `NOTION_NOTES_DB_ID`.

La base contient : Titre, Dossier, Créée le, Modifiée le, Photos, ID Apple, Source.

### 4. Autoriser l'accès à Notes.app

Le premier lancement déclenche une demande d'autorisation macOS. Répondre oui.

```bash
python3 scripts/apple-notes-to-notion.py --limit 3
```

Si l'autorisation a été refusée : Réglages Système > Confidentialité et sécurité >
Automatisation > Terminal (ou l'app utilisée) > cocher Notes.

### 5. Archivage complet puis cron

```bash
python3 scripts/apple-notes-to-notion.py     # première passe complète
bash scripts/crontab-setup.sh                # installe le cron toutes les 6h
```

Pour le cron, macOS demande en plus l'accès complet au disque pour `/usr/sbin/cron`
(Réglages Système > Confidentialité et sécurité > Accès complet au disque).

## Utilisation courante

```bash
python3 scripts/apple-notes-to-notion.py             # notes nouvelles ou modifiées
python3 scripts/apple-notes-to-notion.py --dry-run   # simulation, rien n'est écrit
python3 scripts/apple-notes-to-notion.py --limit 5   # test sur 5 notes
python3 scripts/apple-notes-to-notion.py --full      # tout repousser
```

Depuis Claude Code : `/archive-notes`.

## Ce que le pipeline sait faire

- Titres, paragraphes, listes à puces et numérotées, cases à cocher, citations
- Gras, italique, souligné, barré, code, liens
- Photos et pièces jointes envoyées directement dans Notion via son API d'upload
- Conversion HEIC vers JPEG avec `sips` (natif macOS), Notion affiche mal le HEIC
- Réduction automatique des images au-delà de 20 Mo, limite d'un upload simple Notion
- Reprise : une passe interrompue reprend là où elle s'est arrêtée

## Limites connues, à savoir avant de lancer

**Position des photos dans le texte.** AppleScript donne le texte d'un côté et les pièces
jointes de l'autre, sans dire où chaque image se trouvait dans le flux. Les photos sont donc
regroupées en fin de page sous un titre "Photos et pièces jointes". Pour une restitution au
pixel près il faudrait parser directement `NoteStore.sqlite` (via
[apple_cloud_notes_parser](https://github.com/threeplanetssoftware/apple_cloud_notes_parser)),
au prix d'une dépendance Ruby et d'une sensibilité aux changements de format Apple.

**Notes verrouillées.** Les notes protégées par mot de passe sont inaccessibles à AppleScript.
Elles sont comptées et signalées dans le rapport, pas archivées. Il faut les déverrouiller
dans Notes.app pour qu'elles passent.

**Tableaux et dessins.** Les tableaux Notes.app arrivent aplatis en paragraphes. Les croquis
Apple Pencil sont exportés comme pièces jointes image quand Notes.app les expose.

**Le Mac doit être allumé.** Le cron ne tourne pas si la machine est éteinte. Au réveil, la
passe suivante rattrape tout ce qui a changé entre-temps.

## Dépannage

| Symptôme | Cause probable |
|----------|----------------|
| `execution error: -1743` | Autorisation Automatisation > Notes refusée |
| `Notion 404 sur /databases/...` | Base non partagée avec l'intégration |
| `Notion 400 file_upload` | Token sans droit d'insertion de contenu, ou version d'API trop ancienne (ajuster `NOTION_VERSION` dans `.env`) |
| Photos absentes | Pièce jointe d'un type que Notes.app refuse d'exporter, voir le rapport |
| Script qui s'arrête sur une note | Le rapport et l'état sont sauvegardés, relancer reprend la suite |
