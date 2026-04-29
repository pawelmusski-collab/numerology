from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import async_session, create_booking
from keyboards import get_booking_time_menu, get_cancel_menu, get_confirm_booking_menu
from config import SPECIALIST_USERNAME, ADMIN_ID

router = Router()


class BookingStates(StatesGroup):
    waiting_for_time = State()
    waiting_for_contact = State()
    confirming = State()


TIME_LABELS = {
    "time_morning": "🌅 Утро (9:00–12:00)",
    "time_afternoon": "☀️ День (12:00–17:00)",
    "time_evening": "🌆 Вечер (17:00–21:00)",
    "time_custom": "💬 Индивидуально",
}


@router.callback_query(F.data == "book_specialist")
async def cb_book_specialist(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BookingStates.waiting_for_time)
    await callback.message.answer(
        "📅 *Запись к нумерологу*\n\n"
        "Выбери удобное время для консультации:",
        parse_mode="Markdown",
        reply_markup=get_booking_time_menu(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("time_"))
async def cb_select_time(callback: CallbackQuery, state: FSMContext):
    time_label = TIME_LABELS.get(callback.data, "Не указано")
    await state.update_data(preferred_time=time_label)
    await state.set_state(BookingStates.waiting_for_contact)

    await callback.message.answer(
        f"✅ Выбрано: *{time_label}*\n\n"
        "📱 Напиши свой контакт для связи:\n"
        "_(телефон, Telegram username или email)_",
        parse_mode="Markdown",
        reply_markup=get_cancel_menu(),
    )
    await callback.answer()


@router.message(BookingStates.waiting_for_contact)
async def handle_contact(message: Message, state: FSMContext):
    contact = message.text.strip()
    data = await state.get_data()
    preferred_time = data.get("preferred_time", "Не указано")

    await state.update_data(contact_info=contact)
    await state.set_state(BookingStates.confirming)

    await message.answer(
        "📋 *Проверь данные записи:*\n\n"
        f"🕐 Удобное время: *{preferred_time}*\n"
        f"📱 Контакт: *{contact}*\n\n"
        "Всё верно?",
        parse_mode="Markdown",
        reply_markup=get_confirm_booking_menu(),
    )


@router.callback_query(F.data == "confirm_booking")
async def cb_confirm_booking(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    preferred_time = data.get("preferred_time", "Не указано")
    contact_info = data.get("contact_info", "Не указано")

    async with async_session() as session:
        await create_booking(
            session,
            user_id=callback.from_user.id,
            preferred_time=preferred_time,
            contact_info=contact_info,
        )

    await state.clear()

    # Уведомляем администратора
    try:
        user = callback.from_user
        admin_text = (
            f"🔔 *Новая запись!*\n\n"
            f"👤 Пользователь: {user.first_name or ''} {user.last_name or ''}\n"
            f"🆔 ID: `{user.id}`\n"
            f"📎 Username: @{user.username or 'нет'}\n"
            f"🕐 Время: {preferred_time}\n"
            f"📱 Контакт: {contact_info}"
        )
        await callback.bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")
    except Exception:
        pass  # Не прерываем флоу если уведомление не дошло

    await callback.message.answer(
        "🎉 *Запись оформлена!*\n\n"
        f"Специалист свяжется с тобой по указанному контакту в ближайшее время.\n\n"
        f"Если хочешь написать напрямую: {SPECIALIST_USERNAME}",
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "cancel_booking")
async def cb_cancel_booking(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "❌ Запись отменена. Если передумаешь — нажми кнопку снова.",
    )
    await callback.answer()
