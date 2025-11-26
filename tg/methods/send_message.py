"""Send msg to telegram."""

from __future__ import annotations

from typing import TYPE_CHECKING, Union
import re

from loguru import logger
from aiogram import Bot
from aiogram.types import InputMediaDocument, InputMediaPhoto

# Import TestMessage directly to avoid TYPE_CHECKING issues
try:
    from max.test_message_types import TestMessage
except ImportError:
    TestMessage = None

if TYPE_CHECKING:
    from max.max_types import Message as MaxMessage


def escape_telegram_special_chars(text: str) -> str:
    """
    Escape only the special characters that Telegram API requires to be escaped
    when using MarkdownV2 parse mode.
    
    Args:
        text: Original text
        
    Returns:
        str: Text with escaped special characters
    """
    # Only escape characters that are required for MarkdownV2
    # Based on Telegram Bot API documentation
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    # First escape backslashes to prevent double-escaping
    text = text.replace('\\', '\\\\')
    
    # Then escape each special character with preceding backslash
    for char in special_chars:
        if char in text:
            text = text.replace(char, f'\\{char}')
    
    return text


async def gen_tg_msg(msg: Union[MaxMessage, "TestMessage"]) -> tuple[dict, callable]:
    """Generate telegram message."""
    text = await msg.get_tg_text(msg.chat_title)
    # Escape special characters to avoid Telegram parsing errors
    text = escape_telegram_special_chars(text)
    media = msg.media
    commands = []

    if media:
        types = {}

        input_media = {
            "doc": InputMediaDocument,
            "photo": InputMediaPhoto,
            "sticker": InputMediaPhoto,
        }

        for attach in media:
            media_type = attach[0]

            if media_type != "video":
                types[media_type] = types.get(media_type, [])
                types[media_type].append(
                    input_media[media_type](
                        media=attach[1],
                    ),
                )

        if all(x == "video" for x in types.keys()):  # noqa: SIM118
            commands.append(({"text": text}, Bot.send_message))
        else:
            types[next(iter(types.keys()))][0].caption = text
            for i in types.values():
                if len(i) > 1:
                    args = {"media": i}
                    command = Bot.send_media_group
                    commands.append((args, command))
                else:
                    command = None
                    match i[0].type:
                        case "document":
                            command = Bot.send_document
                        case "sticker":
                            command = Bot.send_photo
                        case "photo":
                            command = Bot.send_photo

                    kwargs = {
                        i[0].type: i[0].media,
                        "caption": i[0].caption,
                        }
                    commands.append((kwargs, command))
    else:
        commands.append(({"text": text}, Bot.send_message))
    return commands


async def send_message(
    bot: Bot,
    msg: Union[MaxMessage, "TestMessage"],
    tg_chat_id: int,
    tg_topic_id: int | None = None,
) -> None:
    """Send message to telegram."""
    try:
        # Determine source type
        if TestMessage is not None and isinstance(msg, TestMessage):
            source_type = "Test"
        elif hasattr(msg, 'event_id'):
            source_type = "Sferum"
        else:
            source_type = "Max"
        
        # Log message forwarding details
        logger.info(
            f"📤 Пересылка сообщения: {source_type} → Telegram | "
            f"Чат: {getattr(msg, 'chat_title', 'Unknown')} ({getattr(msg, 'chat_id', 'Unknown')}) | "
            f"Автор: {getattr(msg, 'from_user', 'Unknown')} | "
            f"Топик: {tg_topic_id} | "
            f"Длина: {len(getattr(msg, 'text', ''))} символов"
        )
        
        # For TestMessage, create simple text command
        if TestMessage is not None and isinstance(msg, TestMessage):
            # Escape special characters in TestMessage text
            escaped_text = escape_telegram_special_chars(msg.text)
            commands = [({"text": escaped_text}, Bot.send_message)]
        else:
            commands = await gen_tg_msg(msg)

        for i, message in enumerate(commands):
            sent_message = await message[1](bot, tg_chat_id, message_thread_id=tg_topic_id, **message[0])
            
            # Log successful delivery
            logger.success(
                f"✅ Сообщение успешно доставлено: {source_type} → Telegram | "
                f"Message ID: {sent_message.message_id} | "
                f"Чат: {getattr(msg, 'chat_title', 'Unknown')} | "
                f"Топик: {tg_topic_id} | "
                f"Часть: {i+1}/{len(commands)}"
            )
            
    except Exception as e:
        source_type = "Sferum" if hasattr(msg, 'event_id') else "Max"
        logger.error(f"❌ Критическая ошибка при пересылке сообщения: {e}")
        logger.error(f"   Детали: {source_type} → Telegram | Чат: {getattr(msg, 'chat_title', 'Unknown')} | Топик: {tg_topic_id}")