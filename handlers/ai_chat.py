import json
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from openai import AsyncOpenAI

from config import OPENAI_API_KEY
from keyboards import get_main_menu, get_ai_end_menu, get_ai_confirm_menu
from database import async_session, get_user

router = Router()
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """Ты — тёплый, внимательный ИИ-ассистент нумеролога Оли Велент.
Твоя задача — помочь человеку осознать и сформулировать свой запрос к консультанту по нумерологии.

Стиль общения:
- Тёплый, живой, без пафоса и давления
- Говоришь на «ты», мягко и с интересом к человеку
- Задаёшь уточняющие вопросы, как опытный коуч — не допрашиваешь, а исследуешь вместе
- Используешь рефлексию: «Я правильно понимаю, что...»
- Короткие ответы — не более 3-4 предложений
- В конце каждого ответа — один вопрос, не несколько
- Никогда не даёшь советов и не интерпретируешь числа самостоятельно — это работа консультанта
- Если человек спрашивает о числах или матрице — отвечаешь коротко (1-2 предложения) и мягко возвращаешь к его запросу
- Иногда делишься тёплым наблюдением: «Знаешь, это очень частый вопрос...» или «Интересно, что ты это замечаешь...»

Твои ограничения:
- Не более 10 ответов на вопросы по расчётам/матрице — после этого предлагаешь живую консультацию
- Не более 5 уточняющих вопросов для прояснения запроса клиента
- После 5 вопросов — формулируешь запрос и предлагаешь подтвердить

Когда запрос сформулирован — завершаешь своё сообщение строго в таком формате (в самом конце):
ЗАПРОС_СФОРМУЛИРОВАН: [краткая формулировка запроса клиента одним предложением]

Важно: никогда не упоминай названия конкретных нумерологических систем. Говори просто «нумерология» или «твои расчёты».
"""


class AIState(StatesGroup):
    chatting = State()


def _count_ai_messages(history: list) -> tuple[int, int]:
    ai_messages = [m for m in history if m["role"] == "assistant"]
    question_count = sum(1 for m in ai_messages if "?" in m["content"])
    calc_answers = sum(1 for m in ai_messages if any(
        word in m["content"].lower()
        for word in ["число", "матриц", "цифр", "расчёт", "ячейк", "психоматриц"]
    ))
    return question_count, calc_answers


async def _get_user_context(user_id: int) -> str:
    try:
        async with async_session() as session:
            user = await get_user(session, user_id)
            if user and user.birth_date and user.belova_number:
                return (
                    f"\nДанные клиента: дата рождения {user.birth_date}, "
                    f"число по нумерологии: {user.belova_number}. "
                    f"Используй это как контекст, но не называй систему по имени."
                )
    except Exception:
        pass
    return ""


async def _ask_openai(history: list, user_context: str) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT + user_context}] + history
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=400,
        temperature=0.85,
    )
    return response.choices[0].message.content.strip()


@router.callback_query(F.data == "talk_to_ai")
async def cb_start_ai(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AIState.chatting)
    user_context = await _get_user_context(callback.from_user.id)
    first_message = (
        "Привет! Я здесь, чтобы помочь тебе разобраться, с чем именно ты хочешь прийти на консультацию.\n\n"
        "Расскажи — что тебя привело сюда? Что сейчас больше всего занимает твои мысли или вызывает вопросы?"
    )
    history = [{"role": "assistant", "content": first_message}]
    await state.update_data(history=history, user_context=user_context)
    await callback.message.answer(
        f"🤖 *ИИ-ассистент*\n\n{first_message}",
        parse_mode="Markdown",
        reply_markup=get_ai_end_menu(),
    )
    await callback.answer()


@router.message(AIState.chatting)
async def handle_ai_message(message: Message, state: FSMContext):
    data = await state.get_data()
    history: list = data.get("history", [])
    user_context: str = data.get("user_context", "")
    user_text = message.text.strip()
    history.append({"role": "user", "content": user_text})

    _, calc_count = _count_ai_messages(history)

    if calc_count >= 10:
        await state.clear()
        await message.answer(
            "🌟 Я вижу, что у тебя много вопросов — это здорово!\n\n"
            "Думаю, настало время поговорить с консультантом вживую — "
            "она сможет разобрать всё глубоко и лично для тебя. 🙂",
            reply_markup=get_main_menu(),
        )
        return

    try:
        await message.bot.send_chat_action(message.chat.id, "typing")
        ai_reply = await _ask_openai(history, user_context)

        if "ЗАПРОС_СФОРМУЛИРОВАН:" in ai_reply:
            parts = ai_reply.split("ЗАПРОС_СФОРМУЛИРОВАН:")
            clean_reply = parts[0].strip()
            formulated = parts[-1].strip()

            history.append({"role": "assistant", "content": ai_reply})
            await state.update_data(history=history, formulated_request=formulated)

            if clean_reply:
                await message.answer(f"🤖 {clean_reply}", parse_mode="Markdown")

            await message.answer(
                f"📝 *Итак, твой запрос к консультанту:*\n\n_{formulated}_\n\n"
                "Я правильно тебя понял?",
                parse_mode="Markdown",
                reply_markup=get_ai_confirm_menu(),
            )
            return

        history.append({"role": "assistant", "content": ai_reply})
        await state.update_data(history=history)
        await message.answer(
            f"🤖 {ai_reply}",
            parse_mode="Markdown",
            reply_markup=get_ai_end_menu(),
        )

    except Exception:
        await message.answer(
            "Упс, что-то пошло не так. Попробуй ещё раз или вернись в главное меню.",
            reply_markup=get_main_menu(),
        )
        await state.clear()


@router.callback_query(F.data == "ai_confirm_request")
async def cb_confirm_request(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "✨ Отлично! Теперь ты можешь записаться к консультанту — "
        "она уже будет знать, над чем вы будете работать вместе. 🙂",
        reply_markup=get_main_menu(),
    )
    await callback.answer()


@router.callback_query(F.data == "ai_rephrase")
async def cb_rephrase(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    history: list = data.get("history", [])
    history.append({"role": "user", "content": "Нет, формулировка не совсем точная. Давай уточним."})
    await state.update_data(history=history)
    await callback.message.answer(
        "🤖 Хорошо, давай уточним. Что именно хочется изменить или добавить?",
        reply_markup=get_ai_end_menu(),
    )
    await callback.answer()


@router.callback_query(F.data == "ai_end")
async def cb_end_ai(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "Хорошо, возвращаемся 🙂 Если захочешь продолжить — нажми «Поговорить с ИИ» снова.",
        reply_markup=get_main_menu(),
    )
    await callback.answer()
