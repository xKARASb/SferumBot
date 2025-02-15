"""Send msg to telegram."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from aiogram import Bot
from aiogram.types import InputMediaAudio, InputMediaDocument, InputMediaPhoto

if TYPE_CHECKING:
    from vk.types import Message as VkMessage


def gen_tg_msg(msg: VkMessage) -> tuple[dict, callable]:
    """Generate telegram message."""
    text = msg.get_tg_text(msg.chat_title)
    media = msg.media
    commands = []

    if media:
        types = {}

        input_media = {
            "photo":InputMediaPhoto,
            "doc": InputMediaDocument,
            "audio": InputMediaAudio,
        }

        for attach in media:
            if attach[0] == "video":
                continue
            types[attach[0]] = types.get(attach[0], [])
            types[attach[0]].append(
                input_media[attach[0]](
                    media=attach[1],
                ),
            )

        types[list(types.keys())[0]][0].caption = text
        for i in types.keys():
            if len(types[i]) > 1:
                args = {"media": types[i]}
                command = Bot.send_media_group
                commands.append((args, command))
            else:
                command = None
                match types[i][0].type:
                    case "document":
                        command = Bot.send_document
                    case "photo":
                        command = Bot.send_photo

                kwargs = {
                    types[i][0].type: types[i][0].media,
                    "caption": types[i][0].caption,
                    }
                commands.append((kwargs, command))
    else:
        commands.append(({"text": text}, Bot.send_message))
    return commands

async def send_message(
    bot: Bot,
    msg: VkMessage,
    tg_chat_id: int,
    tg_topic_id: int | None = None,
) -> None:
    """Send message to telegram."""
    commands = gen_tg_msg(msg)

    for message in commands:
        await message[1](bot, tg_chat_id, message_thread_id=tg_topic_id, **message[0])
