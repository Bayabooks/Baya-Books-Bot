import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TELEBIRR_PHONE = os.getenv("TELEBIRR_PHONE", "0912338058")
TELEBIRR_NAME = os.getenv("TELEBIRR_NAME", "Michael Getachew")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "baya_books")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "bayabooks").lower()
PRICE_SINGLE = int(os.getenv("PRICE_SINGLE", "10"))
DB_PATH = os.getenv("DB_PATH", "baya_books.db")
