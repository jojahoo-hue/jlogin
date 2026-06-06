#!/usr/bin/env python3
"""
Jarvis Telegram Bot — Assistant vocal et textuel de Njaho.
Tourne en continu sur le Mac. Connecte Telegram à Claude (Anthropic API).

Prérequis :
  pip install python-telegram-bot anthropic python-dotenv pyttsx3 openai-whisper

Variables d'environnement (.env) :
  TELEGRAM_BOT_TOKEN   = token du bot (depuis @BotFather)
  TELEGRAM_CHAT_ID     = ton chat ID Telegram (depuis @userinfobot)
  ANTHROPIC_API_KEY    = clé API Anthropic (console.anthropic.com)
"""

import asyncio
import logging
import os
import tempfile
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

try:
    import anthropic
    from telegram import Update, Voice
    from telegram.ext import (
        Application, CommandHandler, MessageHandler,
        filters, ContextTypes
    )
except ImportError:
    print("Dépendances manquantes. Lancer :")
    print("pip install python-telegram-bot anthropic python-dotenv")
    exit(1)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).parent.parent
CONTEXT_FILE = ROOT / "context" / "CONTEXT.md"
HISTORY_FILE = ROOT / "context" / "HISTORY.md"
CLAUDE_MD = ROOT / "CLAUDE.md"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")

if not all([TELEGRAM_TOKEN, ANTHROPIC_KEY]):
    print("Variables manquantes dans .env : TELEGRAM_BOT_TOKEN, ANTHROPIC_API_KEY")
    exit(1)

claude = anthropic.Anthropic(api_key=ANTHROPIC_KEY)


def load_jarvis_context() -> str:
    """Charge le contexte Jarvis complet pour chaque requête."""
    parts = []
    for f in [CLAUDE_MD, CONTEXT_FILE]:
        if f.exists():
            parts.append(f.read_text(encoding="utf-8"))
    return "\n\n---\n\n".join(parts)


def ask_claude(user_message: str, system_extra: str = "") -> str:
    """Envoie un message à Claude avec le contexte Jarvis injecté."""
    system = load_jarvis_context()
    if system_extra:
        system += f"\n\n{system_extra}"

    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=system,
        messages=[{"role": "user", "content": user_message}]
    )
    return response.content[0].text


def transcribe_audio(audio_path: str) -> str:
    """Transcrit un fichier audio via Whisper local."""
    try:
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(audio_path, language="fr")
        return result["text"].strip()
    except ImportError:
        return "[Whisper non installé. Lancer : pip install openai-whisper]"
    except Exception as e:
        return f"[Erreur transcription : {e}]"


def speak(text: str) -> bytes | None:
    """Convertit le texte en audio via pyttsx3 (Mac natif)."""
    try:
        import pyttsx3
        import io
        engine = pyttsx3.init()
        engine.setProperty("rate", 180)
        with tempfile.NamedTemporaryFile(suffix=".aiff", delete=False) as f:
            tmp_path = f.name
        engine.save_to_file(text, tmp_path)
        engine.runAndWait()
        with open(tmp_path, "rb") as f:
            audio_bytes = f.read()
        os.unlink(tmp_path)
        return audio_bytes
    except Exception:
        return None


# ─── HANDLERS ─────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Jarvis opérationnel.\n\n"
        "Commandes disponibles :\n"
        "/morning — Veille du jour\n"
        "/agenda — Planifier la semaine\n"
        "/supervision — Centre NOC\n"
        "/prime — Résumé de contexte\n"
        "/pomodoro — Démarrer un Pomodoro\n\n"
        "Ou envoie-moi directement un message texte ou vocal."
    )


async def cmd_morning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Préparation de ta veille matinale...")
    response = ask_claude(
        "Lance la commande /morning : effectue une veille personnalisée selon mon contexte "
        "et propose un focus du jour. Sois concis, format Telegram (sans markdown lourd)."
    )
    await update.message.reply_text(response)


async def cmd_agenda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Planification de la semaine.\n\n"
        "Quels sont tes créneaux disponibles cette semaine ?\n"
        "Y a-t-il une deadline importante ?"
    )


async def cmd_supervision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Centre de supervision NOC.\n\n"
        "1. incident — Traiter un incident en cours\n"
        "2. bilan — Dashboard du jour\n"
        "3. process — Documenter un process\n"
        "4. auto — Opportunités d'automatisation\n\n"
        "Quel mode ?"
    )


async def cmd_prime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = ask_claude(
        "Lance /prime : charge mon contexte et résume en 5 lignes qui je suis, "
        "mes projets actifs et ce qui était en cours. Format Telegram court."
    )
    await update.message.reply_text(response)


async def cmd_pomodoro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pomodoro démarré. Je te rappelle dans 25 minutes.")
    context.job_queue.run_once(
        pomodoro_callback,
        when=25 * 60,
        chat_id=update.effective_chat.id,
        name="pomodoro"
    )


async def pomodoro_callback(context: ContextTypes.DEFAULT_TYPE):
    response = ask_claude(
        "Le Pomodoro de 25 minutes est terminé. Envoie un rappel court et motivant "
        "à Njaho pour qu'il fasse une pause et se recentre. 2 phrases max."
    )
    await context.bot.send_message(chat_id=context.job.chat_id, text=f"⏱ {response}")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Traite les messages texte libres."""
    user_text = update.message.text
    response = ask_claude(user_text)
    # Telegram : max 4096 caractères par message
    if len(response) > 4000:
        for i in range(0, len(response), 4000):
            await update.message.reply_text(response[i:i+4000])
    else:
        await update.message.reply_text(response)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Transcrit le message vocal puis répond avec Claude."""
    await update.message.reply_text("Message vocal reçu, transcription en cours...")

    voice: Voice = update.message.voice
    voice_file = await context.bot.get_file(voice.file_id)

    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as f:
        tmp_path = f.name

    await voice_file.download_to_drive(tmp_path)

    transcription = transcribe_audio(tmp_path)
    os.unlink(tmp_path)

    await update.message.reply_text(f"Transcription : {transcription}")

    response = ask_claude(transcription)
    await update.message.reply_text(response)


# ─── POMODORO AUTOMATIQUE ─────────────────────────────────────────────────────

async def pomodoro_auto(context: ContextTypes.DEFAULT_TYPE):
    """Pomodoro automatique toutes les 25 minutes si CHAT_ID défini."""
    if not CHAT_ID:
        return
    response = ask_claude(
        "Envoie un rappel Pomodoro court à Njaho : pause de 5 minutes et "
        "question de recentrage sur sa priorité du moment. 2 phrases."
    )
    await context.bot.send_message(chat_id=CHAT_ID, text=f"⏱ {response}")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("morning", cmd_morning))
    app.add_handler(CommandHandler("agenda", cmd_agenda))
    app.add_handler(CommandHandler("supervision", cmd_supervision))
    app.add_handler(CommandHandler("prime", cmd_prime))
    app.add_handler(CommandHandler("pomodoro", cmd_pomodoro))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    logger.info("Jarvis Bot démarré.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
