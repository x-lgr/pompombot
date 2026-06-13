import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))
    DATABASE_NAME = "premium_bot.db"
    USERS_TXT_FILE = "users.txt"
    
    # Default start message
    DEFAULT_START_MESSAGE = """Welcome {first_name} 👋

I'm your Premium Bot! Get exclusive access to premium content.

Use /help to see available commands."""
    
    # Default start image (set to None if no default)
    DEFAULT_START_IMAGE = None
    
    # Payment URL template
    PAYMENT_URL_TEMPLATE = "https://redirect-beta-lemon.vercel.app/{upiname}/{bankname}/{amount}"
    
    # Invite link settings
    INVITE_LINK_EXPIRE_SECONDS = 10
