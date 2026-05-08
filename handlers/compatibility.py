from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

from numerology import calculate_belova_number, calculate_numbers
from keyboards import get_main_menu, get_book_menu

router = Router()


class CompatState(StatesGroup):
    waiting_partner = State()


def _compat_card(day: int, month: int, year: int, label: str) -> str:
    n = calculate_numbers(day, month, year)
    main = calculate_belova_number(day, month, year)
    base = n['base']
    base_reduced = sum(int(d) for d in str(base)) if base > 9 else None
    base_str = f"{base}/{base_reduced}" if base_reduced else str(base)

    return (
        f"*{label}*\n"
        f"🎯 Цель: {n['metacycle']}.{base_str}\n"
        f"🧱 Основа: {n['x_number']}.{n['communicative']}\n"
        f"✨ Уровень развития души: {n['soul_level']}"
    )


@router.callback_query(F.data == "compatibility")
async def cb_compatibility(callback: CallbackQuery, state: FSMContext):
    # Достаём дату из state или просим ввести
    data = await state.get_data()
    user_birth = data.get("user_birth")

    if not user_birth:
        await state.set_state(CompatState.waiting_partner)
        await state.update_data(need_self=True)
        await callback.message.answer(
            "📅 Введи свою дату рождения в формате `DD.MM.YYYY`:",
            parse_mode="Markdown",
        )
    else:
        await state.set_state(CompatState.waiting_partner)
        await callback.message.answer(
            "💑 *Совместимость*\n\n"
            "Введи дату рождения партнёра в формате `DD.MM.YYYY`:",
            parse_mode="Markdown",
        )
    await callback.answer()


@router.message(CompatState.waiting_partner, F.text.regexp(r"^\d{2}\.\d{2}\.\d{4}$"))
async def handle_partner_date(message: Message, state: FSMContext):
    data = await state.get_data()
    need_self = data.get("need_self", False)
    date_str = message.text.strip()

    try:
        dt = datetime.strptime(date_str, "%d.%m.%Y")
    except ValueError:
        await message.answer("⚠️ Неверный формат. Попробуй ещё раз: `DD.MM.YYYY`", parse_mode="Markdown")
        return

    if need_self:
        # Сохраняем дату пользователя, просим дату партнёра
        await state.update_data(user_birth=date_str, need_self=False)
        await message.answer(
            "💑 Теперь введи дату рождения партнёра в формате `DD.MM.YYYY`:",
            parse_mode="Markdown",
        )
        return

    # Есть обе даты — считаем
    user_birth = data.get("user_birth")
    await state.clear()

    try:
        udt = datetime.strptime(user_birth, "%d.%m.%Y")
    except Exception:
        await message.answer("Не удалось найти твою дату. Начни с /start.", reply_markup=get_main_menu())
        return

    user_card = _compat_card(udt.day, udt.month, udt.year, f"Ты ({user_birth})")
    partner_card = _compat_card(dt.day, dt.month, dt.year, f"Партнёр ({date_str})")

    await message.answer(
        f"💑 *Расчёт совместимости*\n\n"
        f"{user_card}\n\n"
        f"{partner_card}\n\n"
        f"🔍 Для полной расшифровки совместимости и персональных рекомендаций "
        f"запишись на консультацию к специалисту.",
        parse_mode="Markdown",
        reply_markup=get_book_menu(),
    )
