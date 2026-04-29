import os
from dotenv import load_dotenv
 
load_dotenv()
 
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
DATABASE_URL: str = os.getenv("DATABASE_URL", "").replace(
    "postgresql://", "postgresql+asyncpg://", 1
)
SPECIALIST_USERNAME: str = os.getenv("SPECIALIST_USERNAME", "@specialist")
ADMIN_ID: int = int(os.getenv("ADMIN_ID", "0"))
 
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables")
