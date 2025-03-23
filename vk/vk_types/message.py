"""Get msg."""

from __future__ import annotations
from loguru import logger

import re
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from aiohttp import ClientSession

REFACTOR_REGEX = r"(?<!\\)(\\|_|\*|\[|\]|\(|\)|\~|`|>|#|\+|-|=|\||\{|\}|\.|\!)"


# Вспомогательные функции
async def markdown_escape(text: str) -> str:
    """Escapes markdown."""
    return re.sub(REFACTOR_REGEX, lambda t: "\\" + t.group(), text) + "\n"


async def validate_text(text: str) -> str:
    """Валидирует текст."""
    return "\n".join(text.split("<br>"))


async def parse_attachments(attachments) -> list:
    """Парсит вложения."""
    media = []

    for attach in attachments:
        media_type = attach["type"]
        data = attach[media_type]

        if media_type == "photo":
            media.append((media_type, data["orig_photo"]["url"]))

        elif media_type == "doc":
            media.append((media_type, data["url"]))

        elif media_type == "sticker":
            media.append((media_type, f'https://vk.com/sticker/1-{data["sticker_id"]}-512b'))

        elif media_type == "video":
            media.append((media_type, data["player"]))

    return media


class Message:
    """Get msg."""

    async def async_init(
        self: Self,
        session: ClientSession,
        date,
        from_id: int,
        text: str,
        attachments,
        conversation_message_id: int,
        **kwargs,
    ) -> None:
        """Just async __init__."""
        self.media = []

        self.session = session
        self.__dict__.update(kwargs)
        self.date = date
        self.sender_id = from_id
        self.text = await validate_text(text)
        self.attachments = attachments
        self.chat_msg_id = conversation_message_id
        self.fwd = self.__dict__.get("fwd_messages", None)
        self.full_name = self.sender_id

        if self.__dict__.get("profiles", False):
            await self.__sender_full_name()

        if self.attachments:
            self.media = await parse_attachments(self.attachments)

        if self.fwd:
            await self.__parse_fwds()

        if self.fwd:
            await self.__get_all_media()
        return self

    async def __parse_fwds(self: Self) -> list[Self]:
        _msg = Message()

        self.fwd  = [
            await _msg.async_init(self.session, **msg, profiles=self.profiles)
            for msg in self.fwd
        ]
        return self.fwd

    async def __sender_full_name(self: Self) -> None:
        for profile in self.profiles:
            if profile["id"] == self.sender_id:
                self.first_name = profile["first_name"]
                self.last_name = profile["last_name"]
                self.full_name = f"{self.first_name} {self.last_name}"

    def __repr__(self: Self) -> str:
        sender = self.__dict__.get("full_name", self.sender_id)
        string = f" from {sender}: {self.text}, chat id: {self.id}"
        if self.media:
            string += f", media: {self.media}"
        if self.fwd:
            string += f", fwds: {self.fwd}"
        return string

    async def __get_all_media(self: Self) -> list:
        media = self.media

        if self.fwd:
            for attach in self.fwd:
                media.extend(await Message.__get_all_media(attach))

        return media

    async def get_tg_text(
        self: Self, chat_title: str | None = "", fwd_depth: int | None = 0,
    ) -> str:
        """Build telegram msg."""
        # Формируем сообщение
        text = "".join([
            "*",
            await markdown_escape(
                f'{f"{chat_title}\n" if chat_title else ""}{self.full_name}:',
            ),
            "*",
            await markdown_escape(f"{self.text}"),
        ])

        # Вложения (фото, видео, документы)  # noqa: ERA001
        if self.attachments:
            text += " ".join([
                f"*{x[0]}*" if x[0] != "video" else f"[{x[0]}]({x[1]})"
                for x in self.media
            ])
            text += "\n"

        # Пересланные сообщения (forward)
        if self.fwd:
            x = [
                    await msg.get_tg_text(
                        msg.__dict__.get("chat_title", ""), fwd_depth=fwd_depth + 1,
                    ) for msg in self.fwd
                ]
            logger.debug(x)
            text += "".join(x)

        # Возвращаем текст сообщения
        return text
