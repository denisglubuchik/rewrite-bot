from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.services.users import UsersService

router = Router(name="survey")

LEX = {
    "user_goals": "Расскажи немного о себе и для каких целей ты будешь использовать бота\n"
                  "Это поможет сделать мои ответы более подходящими для тебя",
    "ask_telegram_channel": "Спасибо за ответ!\n\n"
                            "Вы можете добавить свой Telegram канал для пересылки рерайтов.\n\n"
                            "Для этого необходимо:\n"
                            "1. Добавить бота в свой канал как администратора\n"
                            "2. Отправить мне ID вашего канала\n\n"
                            "ID канала можно найти, в адресной строке в браузере, когда открыт ваш канал. "
                            "ID обычно начинается с символа '-' и состоит из цифр, например: -1001234567890",
    "channel_saved": "Канал успешно сохранен! Теперь вы можете пересылать тексты в свой канал.",
    "invalid_channel": "Похоже, формат ID канала неверный или бот не имеет доступа к каналу. "
                       "Пожалуйста, убедитесь, что бот добавлен в канал и имеет права администратора, "
                       "затем отправьте корректный ID канала.",
    "help": "В этом боте присутствует следующий функционал:\n"
            "/rewrite - рерайт текста\n"
            "/summary - саммари текста\n"
            "/survey - пройти анкету"
}


class SurveyStates(StatesGroup):
    wait_for_user_answer = State()
    wait_for_channel_id = State()


@router.message(Command("survey"))
async def start_survey(message: Message, state: FSMContext):
    await message.answer(text=LEX["user_goals"])
    await state.set_state(SurveyStates.wait_for_user_answer)


@router.message(SurveyStates.wait_for_user_answer)
async def on_wait_for_user_answer(message: Message, state: FSMContext):
    await UsersService.update(model_id=message.from_user.id, user_goals=message.text)

    kb = InlineKeyboardBuilder()
    kb.button(text="Отказаться", callback_data="refuse")

    await message.answer(text=LEX["ask_telegram_channel"], reply_markup=kb.as_markup())
    await state.set_state(SurveyStates.wait_for_channel_id)


@router.message(SurveyStates.wait_for_channel_id)
async def on_wait_for_channel_id(message: Message, state: FSMContext):
    channel_id = message.text.strip()
    if channel_id.startswith('-') and channel_id.replace('-', '').isdigit():
        await UsersService.update(model_id=message.from_user.id, tg_channel_id=channel_id)
        await message.answer(text=LEX["channel_saved"])
        await message.answer(text=LEX["help"])
        await state.clear()
    else:
        await message.answer(text=LEX["invalid_channel"])