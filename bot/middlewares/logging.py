from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Awaitable, Callable

from aiogram import BaseMiddleware

if TYPE_CHECKING:
    from aiogram.types import CallbackQuery, InlineQuery, Message, Update


class LoggingMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        super().__init__()

    def process_message(self, message: Message) -> dict[str, Any]:
        print_attrs: dict[str, Any] = {"chat_type": message.chat.type}

        if message.from_user:
            print_attrs["user_id"] = message.from_user.id
        if message.text:
            print_attrs["text"] = message.text
        if message.video:
            print_attrs["caption"] = message.caption
            print_attrs["caption_entities"] = message.caption_entities
            print_attrs["video_id"] = message.video.file_id
            print_attrs["video_unique_id"] = message.video.file_unique_id
        if message.audio:
            print_attrs["duration"] = message.audio.duration
            print_attrs["file_size"] = message.audio.file_size
        if message.photo:
            print_attrs["caption"] = message.caption
            print_attrs["caption_entities"] = message.caption_entities
            print_attrs["photo_id"] = message.photo[-1].file_id
            print_attrs["photo_unique_id"] = message.photo[-1].file_unique_id

        return print_attrs

    def process_callback_query(self, callback_query: CallbackQuery) -> dict[str, Any]:
        print_attrs: dict[str, Any] = {
            "query_id": callback_query.id,
            "data": callback_query.data,
            "user_id": callback_query.from_user.id,
            "inline_message_id": callback_query.inline_message_id,
        }

        if callback_query.message:
            print_attrs["message_id"] = callback_query.message.message_id
            print_attrs["chat_type"] = callback_query.message.chat.type
            print_attrs["chat_id"] = callback_query.message.chat.id

        return print_attrs

    def process_inline_query(self, inline_query: InlineQuery) -> dict[str, Any]:
        print_attrs: dict[str, Any] = {
            "query_id": inline_query.id,
            "user_id": inline_query.from_user.id,
            "query": inline_query.query,
            "offset": inline_query.offset,
            "chat_type": inline_query.chat_type,
            "location": inline_query.location,
        }

        return print_attrs

    async def __call__(
            self,
            handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: dict[str, Any],
    ) -> Any:
        print_attrs: dict = {}

        if event.message:
            message: Message = event.message

            print_attrs = self.process_message(message)

            logger_msg = (
                "received message | "
                + " | ".join(f"{key}: {value}" for key, value in print_attrs.items() if value is not None),
            )
            self.logger.info(*logger_msg)
        elif event.callback_query:
            callback_query: CallbackQuery = event.callback_query

            print_attrs = self.process_callback_query(callback_query)

            logger_msg = (
                "received callback query | "
                + " | ".join(f"{key}: {value}" for key, value in print_attrs.items() if value is not None),
            )
            self.logger.info(*logger_msg)
        elif event.inline_query:
            inline_query: InlineQuery = event.inline_query

            print_attrs = self.process_inline_query(inline_query)

            logger_msg = (
                "received inline query | "
                + " | ".join(f"{key}: {value}" for key, value in print_attrs.items() if value is not None),
            )
            self.logger.info(*logger_msg)

        return await handler(event, data)
