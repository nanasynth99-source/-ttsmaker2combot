import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging to print everything clearly in the Render console
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Fetch secret keys safely - using empty strings as clean fallbacks instead of crashing
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
API_KEY = os.environ.get("REPLICATE_API_TOKEN", os.environ.get("TTSMAKER_API_KEY", ""))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Greets the user when /start is used."""
    await update.message.reply_text(
        "👋 Welcome! Your bot is alive and running on Render!\n\n"
        "✨ Send me a text message or an image to begin."
    )

async def handle_everything(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles messages and provides a diagnostic if keys are missing."""
    
    # Debug safety check: If Render didn't load the keys, tell the user instead of crashing!
    if not TELEGRAM_TOKEN or not API_KEY:
        error_msg = (
            "⚠️ Bot is running, but API keys are missing inside Render settings!\n\n"
            f"• TELEGRAM_TOKEN found: {'✅ Yes' if TELEGRAM_TOKEN else '❌ No'}\n"
            f"• API Key found: {'✅ Yes' if API_KEY else '❌ No'}\n\n"
            "Please check your Render dashboard under the 'Environment' tab."
        )
        await update.message.reply_text(error_msg)
        return

    # --- YOUR BOT WORKFLOW GOES HERE ---
    if update.message.photo:
        await update.message.reply_text("📸 Received your photo! Processing upscale features...")
        # Image upscaling request processing logic can safely run here
    else:
        text = update.message.text
        await update.message.reply_text(f"📝 Received text: '{text}'. Processing text features...")
        # Text processing logic can safely run here

def main() -> None:
    """Starts the bot application."""
    if not TELEGRAM_TOKEN:
        print("❌ CRITICAL ERROR: TELEGRAM_TOKEN is completely empty. Cannot connect to Telegram.")
        print("Please check your Render Environment settings.")
        # We let it pass instead of exiting so Render keeps the process alive for debugging
        return

    # Initialize application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ALL, handle_everything))

    print("🚀 Bot process started successfully! Listening for messages...")
    application.run_polling()

if __name__ == '__main__':
    main()
