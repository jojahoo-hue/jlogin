#!/bin/bash
# Setup de l'environnement remote (code.claude.com) pour Jarvis.
# À coller dans le "script de setup" de la config d'environnement,
# ou à lancer à la main : bash scripts/setup-remote.sh
#
# Installe les dépendances Python des scripts/ (briefing, sync Notion, bot Telegram).
# Les librairies lourdes de transcription vocale (whisper, pyttsx3) sont exclues
# par défaut : décommenter la ligne correspondante dans requirements.txt si besoin.

set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "→ Installation des dépendances Python de Jarvis..."
python3 -m pip install --upgrade pip
python3 -m pip install -r "$ROOT/requirements.txt"

echo "✓ Setup terminé."
echo ""
echo "Rappel : les secrets doivent être déclarés dans la config d'environnement :"
echo "  ANTHROPIC_API_KEY, NOTION_TOKEN, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID"
