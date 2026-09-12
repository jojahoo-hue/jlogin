#!/bin/bash
# Sync automatique Notes Apple → Notion, à lancer par cron sur le Mac.
#
# Installation :
#   bash scripts/crontab-setup.sh        (installe tous les crons Jarvis)
# ou manuellement :
#   crontab -e
#   0 */6 * * * /chemin/vers/jlogin/scripts/apple-notes-sync.sh
#
# Prérequis :
#   - pip3 install requests python-dotenv
#   - .env avec NOTION_TOKEN et NOTION_NOTES_DB_ID
#   - Réglages Système > Confidentialité et sécurité > Automatisation > Notes
#     autorisé pour /usr/sbin/cron (ou Terminal si lancé à la main)
#
# Variables optionnelles :
#   NOTES_SYNC_GIT_PUSH=1   commite et pousse le rapport sur la branche courante

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$ROOT_DIR/scripts/apple-notes-sync.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

cd "$ROOT_DIR" || exit 1

echo "[$TIMESTAMP] Démarrage sync Notes Apple → Notion" >> "$LOG_FILE"

if python3 scripts/apple-notes-to-notion.py >> "$LOG_FILE" 2>&1; then
    echo "[$TIMESTAMP] Sync réussie" >> "$LOG_FILE"

    if [ "${NOTES_SYNC_GIT_PUSH:-0}" = "1" ]; then
        BRANCH=$(git rev-parse --abbrev-ref HEAD)
        if ! git diff --quiet -- context/import/apple-notes-archive.md; then
            git add context/import/apple-notes-archive.md
            git commit -m "Sync Notes Apple $(date '+%Y-%m-%d %H:%M')" >> "$LOG_FILE" 2>&1
            git push origin "$BRANCH" >> "$LOG_FILE" 2>&1 \
                && echo "[$TIMESTAMP] Rapport poussé sur $BRANCH" >> "$LOG_FILE"
        fi
    fi
else
    echo "[$TIMESTAMP] ERREUR sync Notes Apple, voir ci-dessus" >> "$LOG_FILE"

    # Notification Telegram si le bot Jarvis est configuré
    python3 - << 'PYNOTIF' >> "$LOG_FILE" 2>&1
import os
from dotenv import load_dotenv
load_dotenv()
token, chat_id = os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
if token and chat_id:
    import requests
    requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                  json={"chat_id": chat_id,
                        "text": "⚠️ Sync Notes Apple → Notion en échec. Voir scripts/apple-notes-sync.log"})
PYNOTIF
    exit 1
fi

echo "[$TIMESTAMP] Fin sync" >> "$LOG_FILE"
