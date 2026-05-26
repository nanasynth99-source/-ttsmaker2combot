import os
import logging
import requests
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Fetch secret keys securely from Render Environment Variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
# Using Replicate API for image upscaling (Sign up at replicate.com to get a token)
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN") 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🖼️ Welcome to the AI Image Upscaler Bot!\n\n"
        "Send me any low-resolution image, and I will upscale it to high-definition for you."
    )

async def upscale_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Check if a photo was sent
    if not update.message.photo:
        await update.message.reply_text("Please send an actual image file.")
        return

    status_message = await update.message.reply_text("⏳ Downloading your image...")

    # 1. Get the highest resolution version of the photo sent by the user
    photo_file = await update.message.photo[-1].get_file()
    photo_url = photo_file.file_path # Direct URL to the image on Telegram's servers

    await status_message.edit_text("🪄 Upscaling image using AI... this may take a few seconds.")

    # 2. Call Replicate API (Real-ESRGAN model for upscaling)
    # Model: stability-ai/real-esrgan
    replicate_url = "https://api.replicate.com/v1/predictions"
    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "version": "724340e36656bd18d0af74b34b97089ccf8e79e5b7468132cb071db8c1056f70",
        "input": {
            "image": photo_url,
            "scale": 4, # Upscale by 4x
            "face_enhance": True
        }
    }

    try:
        # Start prediction
        response = requests.post(replicate_url, json=payload, headers=headers, timeout=20)
        prediction = response.json()
        
        if "id" not in prediction:
            await status_message.edit_text("❌ AI Upscaling failed. Please check API configuration.")
            return

        prediction_id = prediction["id"]
        status_url = f"{replicate_url}/{prediction_id}"

        # 3. Poll the API until the upscaling is finished
        while True:
            status_check = requests.get(status_url, headers=headers, timeout=10).json()
            status = status_check.get("status")

            if status == "succeeded":
                output_url = status_check["output"]
                await status_message.edit_text("📤 Sending your upscaled image...")
                # Send the final upscaled image back to user
                await update.message.reply_photo(photo=output_url, caption="✅ Here is your 4x upscaled image!")
                await status_message.delete()
                break
            elif status == "failed":
                await status_message.edit_text("❌ Upscaling failed on the AI server.")
                break
            
            time.sleep(2) # Wait 2 seconds before checking status again

    except Exception as e:
        logger.error(f"Error during upscaling: {e}")
        await status_message.edit_text("❌ An error occurred while processing your image.")

def main() -> None:
    if not TELEGRAM_TOKEN or not REPLICATE_API_TOKEN:
        logger.critical("Missing Environment Variables! Check Render configuration.")
        return

    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    # Listen for photos instead of text
    application.add_handler(MessageHandler(filters.PHOTO, upscale_image))

    print("Image Upscaler Bot is starting up...")
    application.run_polling()

if __name__ == '__main__':
    main()
