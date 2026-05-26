import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Fetch secret keys securely from environment variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TTSMAKER_API_KEY = os.environ.get("TTSMAKER_API_KEY")

DEFAULT_VOICE_ID = 777  # Standard English voice ID example
DEFAULT_LANGUAGE = "en" 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Welcome to the TTSMaker Bot!\n\n"
        "Send me any text, and I will convert it into an AI voice using TTSMaker."
    )

async def handle_tts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text_to_convert = update.message.text
    status_message = await update.message.reply_text("⏳ Synthesizing voice... please wait.")

    api_url = "https://api.ttsmaker.com/v2/create-tts-order"
    payload = {
        "api_key": TTSMAKER_API_KEY,
        "text": text_to_convert,
        "voice_id": DEFAULT_VOICE_ID,
        "language": DEFAULT_LANGUAGE,
        "audio_format": "mp3",
        "speed": 1.0,
        "volume": 1.0
    }

    try:
        response = requests.post(api_url, json=payload, timeout=30)
        data = response.json()

        if str(data.get("error_code")) == "0":
            audio_url = data["audio_file_url"]
            await update.message.reply_audio(audio=audio_url, caption="🎵 Generated via TTSMaker")
            await status_message.delete()
        else:
            error_msg = data.get("error_summary", "Unknown API Error")
            await status_message.edit_text(f"❌ TTSMaker Error: {error_msg}")

    except Exception as e:
        logger.error(f"Error during TTS processing: {e}")
        await status_message.edit_text("❌ Something went wrong while generating the audio.")

def main() -> None:
    if not TELEGRAM_TOKEN or not TTSMAKER_API_KEY:
        logger.critical("Missing Environment Variables! Check Render configuration.")
        return

    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tts))

    print("Bot is starting up...")
    application.run_polling()

if __name__ == '__main__':
    main()
