#!/usr/bin/env python3
"""
Génère le briefing matinal Jarvis et le sauvegarde dans context/import/.
Ce script tourne via cron sur le Mac chaque matin à 7h.
Il peut aussi être appelé depuis le hook SessionStart.

Prérequis : pip install anthropic python-dotenv requests
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    import anthropic
    import requests
    from dotenv import load_dotenv
except ImportError:
    print("pip install anthropic python-dotenv requests")
    sys.exit(1)

load_dotenv()

ROOT = Path(__file__).parent.parent
CONTEXT_FILE = ROOT / "context" / "CONTEXT.md"
CLAUDE_MD = ROOT / "CLAUDE.md"
OUTPUT_FILE = ROOT / "context" / "import" / "morning-briefing-latest.md"

ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def load_context() -> str:
    parts = []
    for f in [CLAUDE_MD, CONTEXT_FILE]:
        if f.exists():
            parts.append(f.read_text(encoding="utf-8"))
    return "\n\n---\n\n".join(parts)


def get_crypto_prices() -> str:
    """Récupère les prix BTC et ETH depuis CoinGecko (gratuit, sans clé)."""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": "bitcoin,ethereum", "vs_currencies": "usd,eur", "include_24hr_change": "true"}
        r = requests.get(url, params=params, timeout=5)
        data = r.json()
        btc = data.get("bitcoin", {})
        eth = data.get("ethereum", {})
        btc_change = btc.get("usd_24h_change", 0)
        eth_change = eth.get("usd_24h_change", 0)
        return (
            f"BTC : ${btc.get('usd', 'N/A'):,} ({btc_change:+.1f}% 24h)\n"
            f"ETH : ${eth.get('usd', 'N/A'):,} ({eth_change:+.1f}% 24h)"
        )
    except Exception:
        return "Prix crypto non disponibles (réseau)"


def generate_briefing() -> str:
    if not ANTHROPIC_KEY:
        return "[ANTHROPIC_API_KEY manquant dans .env]"

    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    context = load_context()
    crypto = get_crypto_prices()
    today = datetime.now().strftime("%A %d %B %Y")

    prompt = f"""Tu es Jarvis, l'assistant de Njaho. Génère son briefing matinal du {today}.

Contexte Jarvis :
{context}

Prix crypto en temps réel :
{crypto}

Génère un briefing concis en français avec :
1. Les prix crypto avec signal DCA (acheter / attendre / neutre)
2. Un focus du jour recommandé basé sur ses projets actifs
3. Une seule question pour démarrer la journée avec intention

Maximum 15 lignes. Direct, sans introduction creuse."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text


def save_briefing(briefing: str):
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    content = f"# Briefing matinal — {today}\n\n{briefing}\n"
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(content, encoding="utf-8")
    print(f"Briefing sauvegardé : {OUTPUT_FILE}")


def send_telegram(briefing: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram non configuré, envoi ignoré.")
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        today = datetime.now().strftime("%A %d %B")
        message = f"☀️ Jarvis — {today}\n\n{briefing}"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=10)
        print("Briefing envoyé sur Telegram.")
    except Exception as e:
        print(f"Erreur Telegram : {e}")


def main():
    print(f"Génération du briefing matinal — {datetime.now().strftime('%H:%M')}")
    briefing = generate_briefing()
    save_briefing(briefing)
    send_telegram(briefing)
    print("Terminé.")


if __name__ == "__main__":
    main()
