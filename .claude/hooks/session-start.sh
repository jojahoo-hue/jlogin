#!/bin/bash
# Hook SessionStart — Jarvis
# S'exécute à chaque ouverture d'une session Claude Code.
# Vérifie si un briefing matinal est disponible et l'affiche.

BRIEFING="$CLAUDE_PROJECT_DIR/context/import/morning-briefing-latest.md"

# Afficher le briefing du jour si généré aujourd'hui
if [ -f "$BRIEFING" ]; then
    FILE_DATE=$(date -r "$BRIEFING" "+%Y-%m-%d" 2>/dev/null || stat -f "%Sm" -t "%Y-%m-%d" "$BRIEFING" 2>/dev/null)
    TODAY=$(date "+%Y-%m-%d")
    if [ "$FILE_DATE" = "$TODAY" ]; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "  JARVIS — BRIEFING DU JOUR DISPONIBLE"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        cat "$BRIEFING"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
    fi
fi
