#!/bin/bash
# Configure tous les crons Jarvis sur ton Mac en une seule commande.
# Usage : bash scripts/crontab-setup.sh
#
# Crons installés :
#   07:00 chaque jour  → briefing matinal (Claude API + Telegram)
#   toutes les 2h      → sync Plaud/Notion
#   22:00 chaque jour  → rappel /done via Telegram

JLOGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Dossier Jarvis détecté : $JLOGIN_DIR"

# Sauvegarde du crontab actuel
crontab -l 2>/dev/null > /tmp/current-crontab || true

# Vérifier si les crons Jarvis sont déjà installés
if grep -q "jarvis\|jlogin" /tmp/current-crontab 2>/dev/null; then
    echo "Crons Jarvis déjà installés. Mise à jour..."
    grep -v "jarvis\|jlogin\|morning-briefing\|plaud-auto-sync" /tmp/current-crontab > /tmp/new-crontab || true
else
    cp /tmp/current-crontab /tmp/new-crontab 2>/dev/null || touch /tmp/new-crontab
fi

# Ajouter les crons Jarvis
cat >> /tmp/new-crontab << EOF

# ─── JARVIS — $JLOGIN_DIR ───────────────────────────────────────
# Briefing matinal 7h (Claude API + Telegram notification)
0 7 * * * cd "$JLOGIN_DIR" && python3 scripts/morning-briefing.py >> scripts/morning.log 2>&1

# Sync Plaud/Notion toutes les 2h
0 */2 * * * "$JLOGIN_DIR/scripts/plaud-auto-sync.sh" >> scripts/sync.log 2>&1

# Rappel /done à 22h via Telegram
0 22 * * * cd "$JLOGIN_DIR" && python3 -c "
import os, requests
from dotenv import load_dotenv
load_dotenv()
token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')
if token and chat_id:
    requests.post(f'https://api.telegram.org/bot{token}/sendMessage',
        json={'chat_id': chat_id, 'text': '🌙 Fin de journée. Tape /done pour faire ton bilan.'})
" >> scripts/done-reminder.log 2>&1
# ────────────────────────────────────────────────────────────────

EOF

# Installer le nouveau crontab
crontab /tmp/new-crontab
rm /tmp/current-crontab /tmp/new-crontab

echo ""
echo "✓ Crons Jarvis installés :"
echo "  07:00 → Briefing matinal (Claude + Telegram)"
echo "  */2h  → Sync Plaud/Notion"
echo "  22:00 → Rappel /done (Telegram)"
echo ""
echo "Vérifier avec : crontab -l"
