"""Get msg."""

from __future__ import annotations

import re

import requests
from aiogram.types import BufferedInputFile

REFACTOR_REGEX = r"(?<!\\)(_|\*|\[|\]|\(|\)|\~|`|>|#|\+|-|=|\||\{|\}|\.|\!)"


def markdown_escape(text: str) -> str:
    """Escapes markdown."""
    return re.sub(REFACTOR_REGEX, lambda t: "\\" + t.group(), text) + "\n\n"


class Message:
    """Get msg."""

    def __init__(self, date, from_id: int, text: str, attachments, conversation_message_id, **kwargs):
        self.__dict__.update(kwargs)
        self.date = date
        self.sender_id = from_id
        self.text = self.__validate_text(text)
        self.attachments = attachments
        self.chat_msg_id = conversation_message_id
        self.fwd = self.__dict__.get("fwd_messages", None)
        self.media = []
        self.full_name = self.sender_id

        if self.__dict__.get("profiles", False):
            self.__sender_full_name()
        if self.attachments:
            self.__parse_attachments()
        if self.fwd:
            self.__parse_fwds()
        if self.fwd:
            self.__get_all_media()

    @staticmethod
    def __get_source_link(attach) -> str:
        req = requests.get(attach["url"], timeout=20)
        if "text" in req.headers.get("Content-Type").split("/"):
            url = req.text[
                req.text.find("https:", req.text.find("docUrl")):\
                                req.text.find('",', req.text.find("docUrl"))]
            req = requests.get("".join(url.split("\\")), timeout=20)
            if len(req.content) < 52428800:
                return BufferedInputFile(
                    req.content,
                    filename=req.url[req.url.rfind("/")+1:req.url.find("?")],
                )
        elif "application" in req.headers.get("Content-Type").split("/"):
            return BufferedInputFile(req.content,
                                    filename=req.url[req.url.rfind("/")+1:\
                                                     req.url.find("?")])
        else:
            return attach["url"]

    @staticmethod
    def __get_max_size_photo_url(attach: dict) -> str:
        link = (0, 100)
        lvls = ("w", "z", "y", "r", "q", "p", "o", "x", "m", "s")

        for i in attach["sizes"]:
          if lvls.index(i["type"]) < link[1]:
             link = (i["url"], lvls.index(i["type"]))
        return link[0]

    def __parse_attachments(self) -> list:
        media = []
        parsers = {
            "photo": self.__get_max_size_photo_url,
            "video": lambda x: x["player"],
            "doc": self.__get_source_link,
        }
        for attach in self.attachments:
            media_type = attach["type"]
            if media_type in parsers.keys():
                media.append((media_type, parsers[media_type](attach[media_type])))
        self.media = media
        return media

    def __parse_fwds(self) -> list:
        fwds = []
        for msg in self.fwd:
            fwds.append(Message(**msg, profiles=self.profiles))
        self.fwd = fwds
        return fwds

    def __sender_full_name(self) -> None:
        for profile in self.profiles:
            if profile["id"] == self.sender_id:
                self.first_name = profile["first_name"]
                self.last_name = profile["last_name"]
                self.full_name = f"{self.first_name} {self.last_name}"
                return

    def __repr__(self) -> str:
        sender = self.__dict__.get("full_name", self.sender_id)
        string = f" from {sender}: {self.text}, chat id: {self.chat_id}"
        if self.media:
            string += f", media: {self.media}"
        if self.fwd:
            string += f", fwds: {self.fwd}"
        return string

    @staticmethod
    def __validate_text(text: str) -> str:
        return "\n".join(text.split("<br>"))

    def __get_all_media(self) -> list:
        media = []
        if self.fwd:
            for attach in self.fwd:
                media.extend(Message.__get_all_media(attach))

        return self.media

    def get_tg_text(
        self, chat_title: str | None = "", fwd_depth: int | None = 1,
    ) -> str:
        """Build telegram msg."""
        # Формируем сообщение
        text = "".join([
            "*",
            markdown_escape(
                f'{chat_title}{"\n" if chat_title else ""}{self.full_name}:',
            ),
            "*",
            markdown_escape(f"\n{self.text}"),
        ])

        # Вложения (фото, видео, документы)
        if self.attachments:
            text += "\n".join([
                f"*{x[0]}*" if x[0] != "video" else f"[{x[0]}]({x[1]})"
                for x in self.media
            ])

        # Пересланные сообщения (forward)
        if self.fwd:
            text += "\n".join([
                Message.get_tg_text(msg, fwd_depth=fwd_depth + 1) for msg in self.fwd
            ])

        # Возвращаем текст сообщения
        return text
