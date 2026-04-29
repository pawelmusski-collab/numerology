from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from database import get_or_create_user, async_session

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    async with async_session() as session:
        await get_or_create_user(
            session,
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
        )

    name = message.from_user.first_name or "друг"

    await message.answer(
        f"✨ Привет, {name}!\n\n"
        "Добро пожаловать в нумерологический помощник по системе *Светланы Беловой*.\n\n"
        "Нумерология — это язык чисел, который помогает лучше понять себя: "
        "свои таланты, задачи и жизненный путь.\n\n"
        "📅 Пожалуйста, введи свою *дату рождения* в формате:\n"
        "`DD.MM.YYYY`\n\n"
        "Например: `15.03.1990`",
        parse_mode="Markdown",
    )
