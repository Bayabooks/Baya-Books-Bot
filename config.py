import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TELEBIRR_PHONE = os.getenv("TELEBIRR_PHONE", "0912338058")
TELEBIRR_NAME = os.getenv("TELEBIRR_NAME", "Michael Getachew")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "baya_books")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "bayabooks").lower()
PRICE_SINGLE = 10 # Forced to 10 for testing
DB_PATH = os.getenv("DB_PATH", "baya_books.db")

CBE_ACCOUNT = os.getenv("CBE_ACCOUNT", "1000326477878")
CBE_NAME = os.getenv("CBE_NAME", "Behailu Getachew")

CHAPA_SECRET_KEY = os.getenv("CHAPA_SECRET_KEY", "CHASECK_TEST_xyz")
BASE_URL = os.getenv("BASE_URL", "https://your-bot-url.onrender.com")
