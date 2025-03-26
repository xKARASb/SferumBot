"""Get msg."""

from __future__ import annotations
from loguru import logger

import re
from typing import TYPE_CHECKING, Self
from aiogram.types import BufferedInputFile
import requests

if TYPE_CHECKING:
    from aiohttp import ClientSession

REFACTOR_REGEX = r"(?<!\\)(\\|_|\*|\[|\]|\(|\)|\~|`|>|#|\+|-|=|\||\{|\}|\.|\!)"

class Message:
    """Get msg."""

    async def async_init(
        self: Self,
        session: ClientSession,
        date,
        from_id: int,
        text: str,
        attachments: list,
        conversation_message_id: int,
        **kwargs: dict,
    ) -> Self:
        """Just async __init__."""
        self.media = []

        self.session = session
        self.__dict__.update(kwargs)
        self.date = date
        self.sender_id = from_id
        self.text = await self.__validate_text(text)
        self.attachments = attachments
        self.chat_msg_id = conversation_message_id
        self.fwd = self.__dict__.get("fwd_messages", None)
        self.full_name = self.sender_id

        self.chat_title = self.__dict__.get("chat_title", " ")

        if self.__dict__.get("profiles", False):
            await self.__sender_full_name()

        if self.attachments:
            self.media = await self.__parse_attachments()

        if self.fwd:
           self.fwd = await self.__parse_fwds()

        if self.fwd:
            self.media = await self.__get_all_media()
        return self

    @staticmethod
    async def __get_player(obj: dict) -> str:
        return obj["player"]

    @staticmethod
    async def __get_sticker(obj: dict) -> str:
        return f'https://vk.com/sticker/1-{obj["sticker_id"]}-512b'

    async def __parse_attachments(self) -> list:
        media = []
        parsers = {
            "photo": self.__get_max_size_photo_url,
            "video": self.__get_player,
            "doc": self.__get_source_link,
            "sticker": self.__get_sticker,
        }
        for attach in self.attachments:
            media_type = attach["type"]
            if parsers.get(media_type, False):
                parsed = await parsers[media_type](attach[media_type])
                if media_type == "doc":
                    media_type = parsed[1]
                    parsed = parsed[0]
                media.append(
                    (media_type, parsed),
                    )
        logger.debug(media)
        return media

    @staticmethod
    async def __get_source_link(attach: dict) -> str:
        req = requests.get(attach["url"])  # noqa: ASYNC210, S113
        logger.info(req.headers.get("Content-Type"))
        if req.headers.get("Content-Type") == "text/html; charset=windows-1251":
            return attach["url"], "video"
        elif req.headers.get("Content-Type").split("/")[0] in ("application", "text"):
            if attach["size"] < 52428800:
                return BufferedInputFile(
                    req.content,
                    filename=attach["title"],
                    ), "doc"
            return BufferedInputFile(
                "File is too large to upload to telegram",
                filename="file is too large.txt",
            ), "doc"
        return attach["url"], "doc"

    @staticmethod
    async def __get_max_size_photo_url(attach: dict) -> str:
        link = (0, 100)
        lvls = ("w", "z", "y", "r", "q", "p", "o", "x", "m", "s")

        for i in attach["sizes"]:
            if lvls.index(i["type"]) < link[1]:
                link = (i["url"], lvls.index(i["type"]))
        return link[0]


    async def __parse_fwds(self: Self) -> list[Self]:
        return [
            await Message().async_init(self.session, **msg, profiles=self.profiles)
            for msg in self.fwd
        ]

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
        for msg in self.fwd:
            logger.debug(msg)
            media.extend(msg.media)

        return media

    async def get_tg_text(
        self: Self, chat_title: str | None = "", fwd_depth: int | None = 0,
    ) -> str:
        """Build telegram msg."""
        # Формируем сообщение
        text = "".join([
            "*",
            await self.__markdown_escape(
                f'{f"{chat_title}\n" if chat_title else ""}{self.full_name}:',
            ),
            "*",
            await self.__markdown_escape(f"{self.text}"),
        ])

        # Вложения (фото, видео, документы)  # noqa: ERA001
        if self.attachments:
            logger.debug(self.media)
            text += " ".join([
                f"*{x[0]}*" if x[0] != "video" else f"[{x[0]}]({x[1]})"
                for x in self.media
            ])
            text += "\n"

        # Пересланные сообщения (forward)
        if self.fwd:
            x = [
                    await msg.get_tg_text(
                        msg.chat_title, fwd_depth=fwd_depth + 1,
                    ) for msg in self.fwd
                ]
            logger.debug(x)
            text += "".join(x)

        # Возвращаем текст сообщения
        return text

    @staticmethod
    async def __markdown_escape(text: str) -> str:
        """Escapes markdown."""
        return re.sub(REFACTOR_REGEX, lambda t: "\\" + t.group(), text) + "\n"

    @staticmethod
    async def __validate_text(text: str) -> str:
        """Валидирует текст."""
        return "\n".join(text.split("<br>"))
