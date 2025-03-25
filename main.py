"""Main cycle module."""

from aiogram import Bot
from loguru import logger
from asyncio import sleep
from aiohttp import ClientSession

from tg.methods import send_message, send_error
from vk.vk_types import EventMessage, Message
from vk.methods import get_credentials, get_message, get_user_credentials


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
    tg_topic_id = None,
) -> None:
    """Cycle function."""
    data = {
        "act": "a_check",
        "key": key,
        "ts": ts,
        "wait": 10,
    }

    while True:
        await sleep(.2)
        try:
            async with session.post(f"https://{server}", data=data) as r:
                req = await r.json()

            logger.debug(req)

            if req.get("updates"):
                data["ts"] += 1
                event = req["updates"][0]

                if event[0] == 4:
                    raw_msg = EventMessage(*event)
                    logger.info(f"[MAIN] raw_msg: {raw_msg}")

                    if str(raw_msg.chat_id) in "".join(vk_chat_ids.split()).split(","):
                        logger.debug("[MAIN] allowed chat")

                        _message = await get_message(session, access_token, pts)

                        if _message.get("error"):
                            access_token = (await get_user_credentials(cookie, session)).access_token
                            credentials = await get_credentials(access_token, session)
                            data["ts"] = credentials.ts
                            data["key"] = credentials.key

                            _message = await get_message(session, access_token, pts)

                            logger.error(_message)
                        else:
                            logger.debug(_message)

                        pts += 1

                        message = _message["items"]
                        profile = _message["profiles"]
                        chat_title = _message["title"]

                        chat_title = "" if not chat_title else f"{chat_title}"

                        msg = Message()
                        await msg.async_init(
                            session,
                            **message[-1],
                            profiles=profile,
                            chat_title=chat_title,
                        )
                        await send_message(bot, msg, tg_chat_id, tg_topic_id)
                    else:
                        pts += 1

            is_failed = req.get("failed")

            if is_failed == 1:
                data["ts"] = req["ts"]

            elif is_failed == 2:
                access_token = (await get_user_credentials(cookie)).access_token
                credentials = await get_credentials(access_token)
                data["ts"] = credentials.ts
                data["key"] = credentials.key
        except Exception as e:
            await send_error(bot, tg_chat_id, tg_topic_id)
            logger.exception(e)

