"""Main cycle module for max2tg."""

from loguru import logger
from aiogram import Bot
from aiohttp import ClientSession
from asyncio import sleep



from max.max_types import EventMessage, Message
from tg.methods.send_message import send_message
from tg.methods.send_error import send_error
from max.methods import get_credentials, get_message, get_user_credentials
from max.pymax_client import create_max_client, convert_pymax_to_max_message


async def main(
    session: ClientSession,
    server: str,
    key: str,
    ts: int,
    tg_chat_id: str,
    max_chat_ids: str,
    access_token: str,
    cookie: str,
    pts: int,
    bot: Bot,
    tg_topic_id = None,
) -> None:
    """Main cycle function for max2tg."""
    data = {
        "act": "a_check",
        "key": key,
        "ts": ts,
        "wait": 10,
    }

    allowed_chat_ids = {
        chat_id for chat_id in "".join(max_chat_ids.split()).split(",") if chat_id
    }

    while True:
        await sleep(.2)
        try:
            async with session.post(f"https://{server}", data=data) as r:
                req = await r.json()

            logger.debug(req)

            updates = req.get("updates") or []
            if updates:
                data["ts"] = req["ts"]

                for event in updates:
                    if event[0] != 4:
                        continue

                    raw_msg = EventMessage(*event)
                    logger.info(f"[MAIN] raw_msg: {raw_msg}")

                    if str(raw_msg.chat_id) not in allowed_chat_ids:
                        pts += 1
                        continue

                    logger.debug("[MAIN] allowed chat")

                    _message = await get_message(session, access_token, pts)

                    if _message.get("error"):
                        access_token = (await get_user_credentials(cookie, session)).access_token
                        credentials = await get_credentials(access_token, session)
                        data["ts"] = credentials.ts
                        data["key"] = credentials.key

                        _message = await get_message(session, access_token, pts)

                        if _message.get("error"):
                            logger.error("[MAIN] Failed to fetch Max message after token refresh: {}", _message)
                            pts += 1
                            continue
                    else:
                        logger.debug(_message)

                    message_items = _message.get("items")
                    if not message_items:
                        logger.warning("[MAIN] Empty items payload for event {}", raw_msg)
                        pts = _message.get("new_pts", pts + 1)
                        continue
                    target_message = next(
                        (
                            item for item in reversed(message_items)
                            if item.get("id") == raw_msg.msg_id
                        ),
                        None,
                    )

                    if target_message is None and message_items:
                        target_message = message_items[-1]

                    if target_message is None:
                        logger.warning("[MAIN] Unable to match Max message for event {}", raw_msg)
                        pts = _message.get("new_pts", pts + 1)
                        continue

                    if not isinstance(target_message, dict):
                        logger.warning("[MAIN] Unexpected Max message payload {}", target_message)
                        pts = _message.get("new_pts", pts + 1)
                        continue

                    profile = _message["profiles"]
                    chat_title = _message["title"]
                    pts = _message.get("new_pts", pts + 1)

                    chat_title = "" if not chat_title else f"{chat_title}"

                    msg = Message()
                    await msg.async_init(
                        session,
                        **target_message,
                        profiles=profile,
                        chat_title=chat_title,
                    )
                    await send_message(bot, msg, tg_chat_id, tg_topic_id)

            is_failed = req.get("failed")

            if is_failed == 1:
                data["ts"] = req["ts"]

            elif is_failed == 2:
                access_token = (await get_user_credentials(cookie, session)).access_token
                credentials = await get_credentials(access_token, session)
                data["ts"] = credentials.ts
                data["key"] = credentials.key
        except Exception as e:
            await send_error(bot, tg_chat_id, tg_topic_id)
            logger.exception(e)