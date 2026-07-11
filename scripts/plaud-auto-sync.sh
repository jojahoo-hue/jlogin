#!/bin/bash
# Auto-sync Plaud → Notion → Jarvis
#
# [DEPRECIE 2026-07-11] L'accès Notion principal passe par le connecteur natif
# claude.ai (OAuth). Ce script reste un fallback pour archiver les
# transcriptions Plaud dans context/import/ via git. Ligne cron retirée de
# crontab-setup.sh ; à réactiver manuellement si tu veux l'archivage git.
#
# À lancer via cron sur le Mac toutes les 2 heures
#
# Installation cron (ouvrir Terminal sur Mac) :
#   crontab -e
#   Ajouter : 0 */2 * * * /chemin/vers/jlogin/scripts/plaud-auto-sync.sh
#
# Prérequis :
#   - pip3 install notion-client python-dotenv
#   - Fichier .env avec NOTION_TOKEN à la racine du projet

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$ROOT_DIR/scripts/sync.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] Démarrage sync Plaud → Notion → Jarvis" >> "$LOG_FILE"

cd "$ROOT_DIR"

# Sync Notion (récupère les nouvelles transcriptions Plaud)
if python3 scripts/sync-notion.py >> "$LOG_FILE" 2>&1; then
    echo "[$TIMESTAMP] Sync Notion réussie" >> "$LOG_FILE"

    # Commit et push si des fichiers ont changé
    if git diff --quiet && git diff --cached --quiet; then
        echo "[$TIMESTAMP] Aucun changement à commiter" >> "$LOG_FILE"
    else
        git add context/import/
        git commit -m "Auto-sync Plaud transcriptions $(date '+%Y-%m-%d %H:%M')"
        git push origin HEAD
        echo "[$TIMESTAMP] Push git effectué" >> "$LOG_FILE"
    fi
else
    echo "[$TIMESTAMP] ERREUR sync Notion" >> "$LOG_FILE"
fi

echo "[$TIMESTAMP] Fin sync" >> "$LOG_FILE"
