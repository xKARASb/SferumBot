"""Send msg to telegram."""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger
from aiogram import Bot
from aiogram.types import InputMediaDocument, InputMediaPhoto

if TYPE_CHECKING:
    from vk.vk_types import Message as VkMessage


async def gen_tg_msg(msg: VkMessage) -> tuple[dict, callable]:
    """Generate telegram message."""
    text = await msg.get_tg_text(msg.chat_title)
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
    msg: VkMessage,
    tg_chat_id: int,
    tg_topic_id: int | None = None,
) -> None:
    """Send message to telegram."""
    commands = await gen_tg_msg(msg)

    for message in commands:
        await message[1](bot, tg_chat_id, message_thread_id=tg_topic_id, **message[0])
