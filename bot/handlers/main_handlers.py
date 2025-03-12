from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.core.loader import llm_caller
from bot.services.users import UsersService
from bot.utils.text_files import process_text_file

router = Router()


class RewriteStates(StatesGroup):
    main = State()
    wait_for_text = State()
    wait_for_tone = State()
    wait_for_style = State()


async def send_to_llm(user_id, text, operation_type, custom_params=None):
    user_goals = await UsersService.get_user_goals(user_id)
    if user_goals:
        custom_params["user_goals"] = user_goals

    if operation_type == "summary":
        response = await llm_caller.summarize_text(user_id, text, custom_params)
    else:
        response = await llm_caller.rewrite_text(user_id, text, custom_params)

    return response


async def offer_forward_to_channel(message: Message, user_id: int):
    tg_channel = await UsersService.get_tg_channel_id(user_id)
    if not tg_channel:
        return None
    kb = InlineKeyboardBuilder()
    kb.button(text="Переслать в канал", callback_data=f"forward_to_channel:{message.message_id}")
    kb.button(text="Не пересылать", callback_data="refuse")
    await message.answer("Хотите переслать результат в ваш Telegram канал?", reply_markup=kb.as_markup())



@router.message(Command("rewrite"))
async def on_rewrite_command(message: Message, state: FSMContext):
    await message.answer(text="Введите текст для которого сделать рерайт")
    await state.update_data(operation_type="rewrite", custom_params={})
    await state.set_state(RewriteStates.wait_for_text)


@router.message(Command("summary"))
async def on_summary_command(message: Message, state: FSMContext):
    await message.answer(text="Введите текст для которого сделать саммари")
    await state.update_data(operation_type="summary", custom_params={})
    await state.set_state(RewriteStates.wait_for_text)


@router.message(RewriteStates.wait_for_text, F.text | F.document)
async def on_receive_text(message: Message, state: FSMContext):
    if document := message.document:
        if not document.file_name.endswith(".txt"):
            await message.answer("Пожалуйста, отправьте текстовый файл с расширением .txt")
            return

        file_path = f"temp_{document.file_id}.txt"
        await message.bot.download(document, destination=file_path)
        text = await process_text_file(file_path)
    else:
        text = message.text

    await state.update_data(text=text)

    kb = InlineKeyboardBuilder()
    kb.button(text="Пропустить смену тональности", callback_data="skip_tone")
    kb.button(text="Отказаться от настроек", callback_data="skip_settings")
    kb.adjust(1,1)

    await message.answer(
        "Введите тональность текста (например: формальная, дружелюбная и т.д.) или используйте кнопки ниже",
        reply_markup=kb.as_markup())
    await state.set_state(RewriteStates.wait_for_tone)


@router.callback_query(StateFilter(RewriteStates.wait_for_tone), F.data == "skip_tone")
async def skip_tone_setting(callback: CallbackQuery, state: FSMContext):
    # Создаем клавиатуру с кнопками пропуска
    kb = InlineKeyboardBuilder()
    kb.button(text="Пропустить смену стиля", callback_data="skip_style")

    await callback.message.edit_text(
        "Введите стиль текста (например: деловой, разговорный и т.д.) или используйте кнопки ниже",
        reply_markup=kb.as_markup())
    await state.set_state(RewriteStates.wait_for_style)


@router.callback_query(StateFilter(RewriteStates.wait_for_style), F.data == "skip_style")
async def skip_style_setting(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get("text", "")
    operation_type = data.get("operation_type", "rewrite")
    custom_params = data.get("custom_params", {})

    # Отправляем сообщение о начале обработки
    await callback.message.edit_text("Обрабатываю текст, пожалуйста подождите...")
    response = await send_to_llm(callback.from_user.id, text, operation_type, custom_params)

    # Отправляем результат
    result_message = await callback.message.answer(response)
    await state.set_state(RewriteStates.main)
    await offer_forward_to_channel(result_message, callback.from_user.id)


@router.callback_query(StateFilter(RewriteStates.wait_for_tone, RewriteStates.wait_for_style),
                       F.data == "skip_settings")
async def process_skip_settings(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get("text", "")
    operation_type = data.get("operation_type", "rewrite")

    # Отправляем сообщение о начале обработки
    await callback.message.edit_text("Обрабатываю текст, пожалуйста подождите...")
    response = await send_to_llm(callback.from_user.id, text, operation_type, {})

    # Отправляем результат
    result_message = await callback.message.answer(response)
    await state.set_state(RewriteStates.main)
    await offer_forward_to_channel(result_message, callback.from_user.id)


@router.message(StateFilter(RewriteStates.wait_for_tone))
async def process_tone_input(message: Message, state: FSMContext):
    tone = message.text

    data = await state.get_data()
    custom_params = data.get("custom_params", {})

    custom_params["tone"] = tone
    await state.update_data(custom_params=custom_params)

    # Создаем клавиатуру с кнопками пропуска
    kb = InlineKeyboardBuilder()
    kb.button(text="Пропустить смену стиля", callback_data="skip_style")

    await message.answer("Введите стиль текста (например: деловой, разговорный и т.д.) или используйте кнопки ниже",
                         reply_markup=kb.as_markup())
    await state.set_state(RewriteStates.wait_for_style)


@router.message(StateFilter(RewriteStates.wait_for_style))
async def process_style_input(message: Message, state: FSMContext):
    style = message.text

    data = await state.get_data()
    custom_params = data.get("custom_params", {})
    text = data.get("text", "")
    operation_type = data.get("operation_type", "rewrite")

    custom_params["style"] = style
    await state.update_data(custom_params=custom_params)

    # Отправляем сообщение о начале обработки
    await message.answer("Обрабатываю текст, пожалуйста подождите...")
    response = await send_to_llm(message.from_user.id, text, operation_type, custom_params)

    # Отправляем результат
    result_message = await message.answer(response)
    await state.set_state(RewriteStates.main)
    await offer_forward_to_channel(result_message, message.from_user.id)


@router.callback_query(F.data.startswith("forward_to_channel:"))
async def forward_to_channel(callback: CallbackQuery):
    # Получаем ID сообщения, которое нужно переслать
    message_id = int(callback.data.split(':')[1])

    # Получаем ID канала пользователя
    tg_channel_id = await UsersService.get_tg_channel_id(callback.from_user.id)

    if not tg_channel_id:
        await callback.message.answer("Канал не найден. Пожалуйста, добавьте канал через команду /survey", show_alert=True)
        return

    try:
        # Пересылаем текст в канал
        await callback.bot.copy_message(chat_id=tg_channel_id, from_chat_id=callback.from_user.id, message_id=message_id)

        # Уведомляем пользователя об успешной пересылке
        await callback.answer("Текст успешно отправлен в ваш канал!", show_alert=True)
        await callback.message.edit_text("Текст отправлен в ваш канал")
    except Exception as e:
        # В случае ошибки показываем уведомление
        await callback.answer(f"Ошибка при пересылке: {str(e)}", show_alert=True)
