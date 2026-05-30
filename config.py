import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    BOT_DISPLAY_NAME = os.getenv("BOT_DISPLAY_NAME", "Nudge")
    BOT_USERNAME = os.getenv("BOT_USERNAME", "GetReminded_Bot")

    # Email Settings
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    EMAIL_SERVER = os.getenv("EMAIL_SERVER", "smtp.gmail.com")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))

    # Gemini AI
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # Web Settings for OAuth Callback
    WEB_URL = os.getenv("WEB_URL") # e.g. https://nudge-production.up.railway.app
    PORT = int(os.getenv("PORT", 8080))

    # Check if token exists
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("No TELEGRAM_BOT_TOKEN found in environment. Please check your .env file.")
