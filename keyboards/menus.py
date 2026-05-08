from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 Поговорить с ИИ", callback_data="talk_to_ai")],
        [InlineKeyboardButton(text="📅 Записаться к специалисту", callback_data="book_specialist")],
        [InlineKeyboardButton(text="🔄 Рассчитать другую дату", callback_data="recalculate")],
    ])


def get_after_matrix_menu() -> InlineKeyboardMarkup:
    """Кнопка совместимости появляется под психоматрицей."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💑 Совместимость", callback_data="compatibility")],
    ])


def get_book_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Записаться к специалисту", callback_data="book_specialist")],
        [InlineKeyboardButton(text="🔄 Рассчитать другую дату", callback_data="recalculate")],
    ])


def get_booking_time_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌅 Утро (9:00–12:00)", callback_data="time_morning")],
        [InlineKeyboardButton(text="☀️ День (12:00–17:00)", callback_data="time_afternoon")],
        [InlineKeyboardButton(text="🌆 Вечер (17:00–21:00)", callback_data="time_evening")],
        [InlineKeyboardButton(text="💬 Обсудить индивидуально", callback_data="time_custom")],
    ])


def get_cancel_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_booking")],
    ])


def get_confirm_booking_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить запись", callback_data="confirm_booking")],
        [InlineKeyboardButton(text="✏️ Изменить время", callback_data="book_specialist")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_booking")],
    ])


def get_ai_end_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Записаться к специалисту", callback_data="book_specialist")],
        [InlineKeyboardButton(text="🚪 Завершить разговор", callback_data="ai_end")],
    ])


def get_ai_confirm_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, всё верно", callback_data="ai_confirm_request")],
        [InlineKeyboardButton(text="✏️ Уточнить формулировку", callback_data="ai_rephrase")],
        [InlineKeyboardButton(text="📅 Записаться к специалисту", callback_data="book_specialist")],
    ])
