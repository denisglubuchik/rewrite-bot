import os

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.filters import Command

from llm.caller import send_message_to_model

router = Router()


class RewriteStates(StatesGroup):
    main = State()
    rewrite_wait_for_text = State()
    summary_wait_for_text = State()


@router.message(Command("rewrite"))
async def on_rewrite_command(message: Message, state: FSMContext):
    await message.answer(text="Введите текст для которого сделать рерайт")
    await state.set_state(RewriteStates.rewrite_wait_for_text)


async def process_text_file(file_path) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
        return text
    finally:
        os.remove(file_path)


@router.message(RewriteStates.rewrite_wait_for_text, F.text | F.document)
async def on_receive_text_to_rewrite(message: Message, state: FSMContext):
    if document := message.document:
        if not document.file_name.endswith(".txt"):
            await message.answer("Пожалуйста, отправьте текстовый файл с расширением .txt")
            return

        file_path = f"temp_{document.file_id}.txt"
        await message.bot.download(document, destination=file_path)
        text = await process_text_file(file_path)
    else:
        text = message.text

    prompt = "Сделай рерайт текста:\n"
    response = await send_message_to_model(text, prompt)
    await message.answer(response)
    await state.set_state(RewriteStates.main)


@router.message(Command("summary"))
async def on_summary_command(message: Message, state: FSMContext):
    await message.answer(text="Введите текст для которого сделать саммари")
    await state.set_state(RewriteStates.summary_wait_for_text)


@router.message(RewriteStates.summary_wait_for_text, F.text | F.document)
async def on_receive_text_to_rewrite(message: Message, state: FSMContext):
    if document := message.document:
        if not document.file_name.endswith(".txt"):
            await message.answer("Пожалуйста, отправьте текстовый файл с расширением .txt")
            return

        file_path = f"temp_{document.file_id}.txt"
        await message.bot.download(document, destination=file_path)
        text = await process_text_file(file_path)
    else:
        text = message.text

    prompt = ("Cократи текст насколько возможно до 3-4 предложений, сохранив его основную суть и ключевые факты. "
              "Упрощай сложные фразы, убирай лишние детали, но не теряй смысл\n\n")
    response = await send_message_to_model(text, prompt)
    await message.answer(response)
    await state.set_state(RewriteStates.main)
