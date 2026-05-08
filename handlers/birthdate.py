import re
from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile

from database import async_session, update_user_numerology
from numerology import (
    calculate_belova_number, get_belova_description,
    calculate_psychomatrix, get_psychomatrix_summary,
    psychomatrix_to_json, calculate_numbers,
    generate_psychomatrix_image,
)
from keyboards import get_main_menu, get_after_matrix_menu

router = Router()


def validate_date(date_str: str) -> datetime | None:
    try:
        return datetime.strptime(date_str, "%d.%m.%Y")
    except ValueError:
        return None


def _format_numbers(n: dict) -> str:
    base = n['base']
    base_reduced = sum(int(d) for d in str(base)) if base > 9 else None
    base_str = f"{base}/{base_reduced}" if base_reduced else str(base)
    return (
        f"🔢 *Метацикл:* {n['metacycle']}\n"
        f"🔢 *Базовое число:* {base_str}\n"
        f"🔢 *Икс число:* {n['x_number']}\n"
        f"🔢 *Коммуникативное:* {n['communicative']}\n"
        f"🔢 *Уровень развития души:* {n['soul_level']}"
    )


@router.message(F.text.regexp(r"^\d{2}\.\d{2}\.\d{4}$"))
async def handle_birthdate(message: Message):
    date_str = message.text.strip()
    dt = validate_date(date_str)

    if not dt or dt.year < 1900 or dt > datetime.now():
        await message.answer("⚠️ Дата некорректна. Формат: `DD.MM.YYYY`", parse_mode="Markdown")
        return

    day, month, year = dt.day, dt.month, dt.year

    main_number = calculate_belova_number(day, month, year)
    desc = get_belova_description(main_number)
    extra = calculate_numbers(day, month, year)
    psycho_counts = calculate_psychomatrix(day, month, year)
    psycho_summary = get_psychomatrix_summary(psycho_counts)
    psycho_json = psychomatrix_to_json(psycho_counts)

    image_buf = generate_psychomatrix_image(psycho_counts, date_str, main_number, extra)
    photo = BufferedInputFile(image_buf.read(), filename="psychomatrix.png")

    async with async_session() as session:
        await update_user_numerology(
            session, user_id=message.from_user.id,
            birth_date=date_str, belova_number=main_number, psychomatrix=psycho_json,
        )

    await message.answer(
        f"🔢 *Твоё нумерологическое число: {main_number}*\n"
        f"_{desc['title']}_\n\n{desc['short']}\n\n"
        f"🏷 Ключевые слова: _{desc['keywords']}_\n\n"
        f"{_format_numbers(extra)}",
        parse_mode="Markdown",
    )

    await message.answer_photo(
        photo=photo,
        caption=f"🔲 *Психоматрица (квадрат Пифагора)*\n\n{psycho_summary}",
        parse_mode="Markdown",
        reply_markup=get_after_matrix_menu(),
    )

    await message.answer(
        "🌟 *Это лишь первый шаг к пониманию себя.*\n\n"
        "Наш специалист проведёт полную нумерологическую консультацию:\n"
        "• Детальный разбор числа личности\n"
        "• Анализ психоматрицы\n"
        "• Числа судьбы, имени и года\n"
        "• Персональные рекомендации\n\n"
        "👇 Выбери действие:",
        parse_mode="Markdown",
        reply_markup=get_main_menu(),
    )


@router.callback_query(F.data == "recalculate")
async def cb_recalculate(callback: CallbackQuery):
    await callback.message.answer("📅 Введи дату рождения в формате `DD.MM.YYYY`:", parse_mode="Markdown")
    await callback.answer()
