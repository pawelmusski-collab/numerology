import json
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import async_session, create_booking, get_user
from keyboards import get_booking_time_menu, get_cancel_menu, get_confirm_booking_menu
from config import SPECIALIST_USERNAME, ADMIN_ID
from numerology import generate_psychomatrix_image

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
    tg_user = callback.from_user

    # Сохраняем запись в БД
    async with async_session() as session:
        await create_booking(
            session,
            user_id=tg_user.id,
            preferred_time=preferred_time,
            contact_info=contact_info,
        )
        # Достаём данные пользователя из БД
        db_user = await get_user(session, tg_user.id)

    await state.clear()

    # Отправляем специалисту карточку клиента
    try:
        # Формируем текст карточки
        name = f"{tg_user.first_name or ''} {tg_user.last_name or ''}".strip() or "Не указано"
        username = f"@{tg_user.username}" if tg_user.username else "нет username"

        belova = db_user.belova_number if db_user else "—"
        birth = db_user.birth_date if db_user else "—"

        card_text = (
            f"🔔 *Новая запись на консультацию!*\n\n"
            f"👤 *Клиент:* {name}\n"
            f"📎 *Telegram:* {username}\n"
            f"🆔 *ID:* `{tg_user.id}`\n"
            f"📱 *Контакт:* {contact_info}\n"
            f"🕐 *Удобное время:* {preferred_time}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📅 *Дата рождения:* {birth}\n"
            f"🔢 *Число Беловой:* {belova}\n"
        )

        # Если есть психоматрица — отправляем картинкой
        if db_user and db_user.psychomatrix and db_user.birth_date and db_user.belova_number:
            try:
                counts = {int(k): v for k, v in json.loads(db_user.psychomatrix).items()}
                image_buf = generate_psychomatrix_image(counts, db_user.birth_date, db_user.belova_number)
                photo = BufferedInputFile(image_buf.read(), filename="psychomatrix.png")
                await callback.bot.send_photo(
                    ADMIN_ID,
                    photo=photo,
                    caption=card_text,
                    parse_mode="Markdown",
                )
            except Exception:
                # Если картинка не получилась — шлём только текст
                await callback.bot.send_message(ADMIN_ID, card_text, parse_mode="Markdown")
        else:
            await callback.bot.send_message(ADMIN_ID, card_text, parse_mode="Markdown")

    except Exception:
        pass  # Не прерываем флоу если уведомление не дошло

    # Отвечаем клиенту
    await callback.message.answer(
        "🎉 *Запись оформлена!*\n\n"
        "Специалист свяжется с тобой по указанному контакту в ближайшее время.\n\n"
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
