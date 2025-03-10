"""Main cycle module."""

from aiogram import Bot
from aiohttp import ClientSession
from loguru import logger

from tg.methods import send_message
from vk.methods import get_credentials, get_message, get_user_credentials
from vk.vk_types import EventMessage, Message


async def main(
    session: ClientSession,
    server: str,
    key: str,
    ts: int,
    tg_chat_id: str,
    vk_chat_ids: str,
    access_token: str,
    cookie: str,
    pts: int,
    bot: Bot,
) -> None:
    """Cycle function."""
    data = {
        "act": "a_check",
        "key": key,
        "ts": ts,
        "wait": 10,
    }
    try:
        while True:
            req = await session.post(f"https://{server}", data=data, timeout=20)
            req = await req.json()

            logger.debug(req)

            if req.get("updates"):
                data["ts"] += 1
                event = req["updates"][0]

                if event[0] == 4:
                    raw_msg = EventMessage(*event)
                    logger.info(f"[MAIN] raw_msg: {raw_msg}")
                    if str(
                        raw_msg.chat_id,
                    ) in "".join(vk_chat_ids.split()).split(","):
                        logger.debug("[MAIN] allowed chat")

                        _message = get_message(access_token, pts)

                        if _message.get("error"):
                            access_token = get_user_credentials(cookie).access_token
                            credentials = get_credentials(access_token)
                            data["ts"] = credentials.ts
                            data["key"] = credentials.key

                            logger.error(_message)
                        else:
                            logger.debug(_message)

                        pts += 1

                        message = _message["items"]
                        profile = _message["profiles"]
                        chat_title = _message["title"]

                        chat_title = "" if not chat_title else f"{chat_title}"

                        msg = Message(
                            **message[-1],
                            profiles=profile,
                            chat_title=chat_title,
                        )
                        await send_message(bot, msg, tg_chat_id)
                    else:
                        pts += 1

            if req.get("failed", False) == 1:
                data["ts"] = req["ts"]
            elif req.get("failed", False) == 2:
                access_token = get_user_credentials(cookie).access_token
                credentials = get_credentials(access_token)
                data["ts"] = credentials.ts
                data["key"] = credentials.key

    except Exception as e:
        logger.error(e)
