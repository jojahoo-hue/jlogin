#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/bot.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "Bot non démarré (pas de PID trouvé)."
    exit 0
fi

PID=$(cat "$PID_FILE")
if kill -0 "$PID" 2>/dev/null; then
    kill "$PID"
    rm "$PID_FILE"
    echo "Jarvis Bot arrêté (PID $PID)."
else
    rm "$PID_FILE"
    echo "Bot déjà arrêté."
fi
