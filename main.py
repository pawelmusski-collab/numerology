import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from database import init_db
from handlers import start_router, birthdate_router, booking_router, ai_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting numerology bot...")
    await init_db()
    logger.info("Database initialized.")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )

    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(start_router)
    dp.include_router(birthdate_router)
    dp.include_router(booking_router)
    dp.include_router(ai_router)

    logger.info("Bot is polling...")
    await dp.start_polling(bot, drop_pending_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
