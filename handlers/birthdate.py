import re
from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile

from database import async_session, update_user_numerology
from numerology import (
    calculate_belova_number,
    get_belova_description,
    calculate_psychomatrix,
    get_psychomatrix_summary,
    psychomatrix_to_json,
    generate_psychomatrix_image,
)
from keyboards import get_main_menu

router = Router()

DATE_PATTERN = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")


def validate_date(date_str: str) -> datetime | None:
    try:
        return datetime.strptime(date_str, "%d.%m.%Y")
    except ValueError:
        return None


@router.message(F.text.regexp(r"^\d{2}\.\d{2}\.\d{4}$"))
async def handle_birthdate(message: Message):
    date_str = message.text.strip()
    dt = validate_date(date_str)

    if not dt:
        await message.answer(
            "⚠️ Неверный формат даты. Попробуй ещё раз:\n`DD.MM.YYYY`\n\nНапример: `15.03.1990`",
            parse_mode="Markdown",
        )
        return

    if dt.year < 1900 or dt > datetime.now():
        await message.answer(
            "⚠️ Дата выглядит некорректной. Проверь год рождения и попробуй снова.",
        )
        return

    day, month, year = dt.day, dt.month, dt.year

    # Расчёты
    belova_number = calculate_belova_number(day, month, year)
    desc = get_belova_description(belova_number)

    psycho_counts = calculate_psychomatrix(day, month, year)
    psycho_summary = get_psychomatrix_summary(psycho_counts)
    psycho_json = psychomatrix_to_json(psycho_counts)

    # Генерируем картинку
    image_buf = generate_psychomatrix_image(psycho_counts, date_str, belova_number)
    photo = BufferedInputFile(image_buf.read(), filename="psychomatrix.png")

    # Сохраняем в БД
    async with async_session() as session:
        await update_user_numerology(
            session,
            user_id=message.from_user.id,
            birth_date=date_str,
            belova_number=belova_number,
            psychomatrix=psycho_json,
        )

    # Часть 1: число по Беловой
    await message.answer(
        f"🔢 *Твоё нумерологическое число: {belova_number}*\n"
        f"_{desc['title']}_\n\n"
        f"{desc['short']}\n\n"
        f"🏷 Ключевые слова: _{desc['keywords']}_",
        parse_mode="Markdown",
    )

    # Часть 2: психоматрица картинкой
    await message.answer_photo(
        photo=photo,
        caption=f"🔲 *Психоматрица (квадрат Пифагора)*\n\n{psycho_summary}",
        parse_mode="Markdown",
    )

    # Часть 3: предложение записаться
    await message.answer(
        "🌟 *Это лишь первый шаг к пониманию себя.*\n\n"
        "Наш специалист проведёт для тебя *полную нумерологическую консультацию*, "
        "которая включает:\n"
        "• Детальный разбор числа личности\n"
        "• Анализ всей психоматрицы\n"
        "• Числа судьбы, имени и года\n"
        "• Персональные рекомендации\n\n"
        "👇 Выбери действие:",
        parse_mode="Markdown",
        reply_markup=get_main_menu(),
    )


@router.callback_query(F.data == "recalculate")
async def cb_recalculate(callback: CallbackQuery):
    await callback.message.answer(
        "📅 Введи новую дату рождения в формате `DD.MM.YYYY`:",
        parse_mode="Markdown",
    )
    await callback.answer()
