from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.services.users import UsersService
from bot.handlers.survey import start_survey

router = Router(name="start")

LEX = {
    "hello": "Привет, это рерайт бот, сначала предлагаю тебе ответить на пару вопросов",
    "help": "В этом боте присутствует следующий функционал:\n"
            "/rewrite - рерайт текста\n"
            "/summary - саммари текста\n"
            "/survey - пройти анкету"
}


@router.message(CommandStart())
async def on_start_command(message: Message):
    if not await UsersService.find_by_id(message.from_user.id):
        await UsersService.insert(id=message.from_user.id, username=message.from_user.username)

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Ответить", callback_data="ask_questions"),
        InlineKeyboardButton(text="Отказаться", callback_data="refuse"),
    )
    await message.answer(LEX["hello"], reply_markup=builder.as_markup())


@router.message(Command("help"))
async def on_help_command(message: Message):
    await message.answer(text=LEX["help"])


@router.callback_query(F.data == "refuse")
async def on_refuse(callback: CallbackQuery):
    await callback.message.delete_reply_markup()
    await callback.message.answer(text=LEX["help"])


@router.callback_query(F.data == "ask_questions")
async def on_ask_questions(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await start_survey(callback.message, state)


@router.message()
async def on_idle_message(message: Message):
    await message.answer(LEX['help'])