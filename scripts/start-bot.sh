#!/bin/bash
# Démarre le bot Jarvis Telegram en arrière-plan sur Mac
# Usage : ./scripts/start-bot.sh
# Stop  : ./scripts/stop-bot.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$ROOT_DIR/scripts/bot.pid"
LOG_FILE="$ROOT_DIR/scripts/bot.log"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "Bot déjà en cours (PID $PID). Lancer stop-bot.sh d'abord."
        exit 1
    fi
fi

cd "$ROOT_DIR"
nohup python3 scripts/telegram-bot.py >> "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"
echo "Jarvis Bot démarré (PID $(cat $PID_FILE))"
echo "Logs : tail -f $LOG_FILE"
