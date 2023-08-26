import logging
import requests

from asyncio import sleep

from vk.methods import get_credentials, get_user_credentials, get_message
from vk.types import EventMessage, Message

from tgBot.methods import send_message

async def main(key, ts, vk_chat_id, access_token, cookie, bot, vk_id):
    while True:
        await sleep(0.1)
        try:
            req = requests.post(f"https://api.vk.me/ruim{vk_id}?version=19&mode=682", data={"act": "a_check", "key": key, "ts": ts, "wait": 10}).json()
            if req.get("updates"):
                ts += 1
                event = req["updates"][0]
                match event[0]:
                    case 10004:
                        raw_message = EventMessage(*event)
                        if raw_message.chat_id == vk_chat_id:
                            message, profile = get_message(access_token, req["pts"]-len(req["updates"]))
                            message = Message(**message[0], profiles=profile)
                            await send_message(bot, message)
                            
            if req.get("failed", False) == 1:
                ts = req["ts"]
            elif req.get("failed", False) == 2:
                credentials = get_credentials(get_user_credentials(cookie))
                ts = credentials["ts"]
                key = credentials["key"]
        except Exception as e:
            logging.exception(e)

