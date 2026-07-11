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

# Réponse vocale (optionnel). Nécessite macOS `say` + `ffmpeg` (brew install ffmpeg).
VOICE_REPLY = os.getenv("VOICE_REPLY", "true").lower() == "true"
TTS_VOICE = os.getenv("TTS_VOICE", "Thomas")  # voix FR macOS

if not all([TELEGRAM_TOKEN, ANTHROPIC_KEY, CHAT_ID]):
    print("Variables manquantes dans .env : TELEGRAM_BOT_TOKEN, ANTHROPIC_API_KEY, TELEGRAM_CHAT_ID")
    print("TELEGRAM_CHAT_ID est requis pour restreindre le bot à ton seul compte.")
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
        model="claude-sonnet-5",
        max_tokens=1500,
        system=system,
        messages=[{"role": "user", "content": user_message}]
    )
    return response.content[0].text


def text_to_voice(text: str) -> str | None:
    """Synthèse vocale d'une réponse en note vocale OGG/Opus.

    Utilise la commande macOS `say` (voix FR native) puis `ffmpeg` pour
    convertir en Opus, format des notes vocales Telegram. Retourne le chemin
    du fichier .ogg, ou None si `say`/`ffmpeg` sont indisponibles (le bot
    répond alors en texte uniquement).
    """
    import shutil
    import subprocess

    if not shutil.which("say") or not shutil.which("ffmpeg"):
        logger.warning("Synthèse vocale ignorée : `say` ou `ffmpeg` introuvable.")
        return None
    try:
        with tempfile.NamedTemporaryFile(suffix=".aiff", delete=False) as f:
            aiff_path = f.name
        ogg_path = aiff_path[:-5] + ".ogg"
        subprocess.run(
            ["say", "-v", TTS_VOICE, "-o", aiff_path, text],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        subprocess.run(
            ["ffmpeg", "-y", "-i", aiff_path, "-c:a", "libopus", "-b:a", "32k", ogg_path],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        os.unlink(aiff_path)
        return ogg_path
    except Exception as e:
        logger.warning(f"Synthèse vocale échouée : {e}")
        return None


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

    # Vocal reçu → réponse aussi en vocal (si activé et outils dispo).
    if VOICE_REPLY:
        # On limite la longueur synthétisée pour garder une note vocale courte.
        voice_text = response if len(response) <= 1200 else response[:1200] + "…"
        ogg_path = text_to_voice(voice_text)
        if ogg_path:
            try:
                with open(ogg_path, "rb") as vf:
                    await update.message.reply_voice(vf)
            finally:
                os.unlink(ogg_path)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Sécurité : le bot ne répond qu'au CHAT_ID de Njaho.
    auth = filters.Chat(chat_id=int(CHAT_ID))

    app.add_handler(CommandHandler("start", cmd_start, filters=auth))
    app.add_handler(CommandHandler("morning", cmd_morning, filters=auth))
    app.add_handler(CommandHandler("agenda", cmd_agenda, filters=auth))
    app.add_handler(CommandHandler("supervision", cmd_supervision, filters=auth))
    app.add_handler(CommandHandler("prime", cmd_prime, filters=auth))
    app.add_handler(CommandHandler("pomodoro", cmd_pomodoro, filters=auth))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & auth, handle_text))
    app.add_handler(MessageHandler(filters.VOICE & auth, handle_voice))

    logger.info("Jarvis Bot démarré.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
