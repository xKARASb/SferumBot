import requests

from os import getenv
from dotenv import load_dotenv

from vk.methods import get_credentials, get_web_token, get_message
from vk.types import EventMessage, Message

load_dotenv()


tg_chat_id = getenv("TG_CHAT_ID")
vk_chat_id = int(getenv("VK_CHAT_ID"))
bot_token = getenv("BOT_TOKEN")
cookie = getenv("AUTH_COOKIE")

access_token = get_web_token(cookie)
credentials = get_credentials(access_token)

ts = credentials["ts"]
key = credentials["key"]

while True:
    req = requests.post("https://api.vk.me/ruim791593813?version=19&mode=682", data={"act": "a_check", "key": key, "ts": ts, "wait": 25}).json()
    if req.get("updates"):
        ts += 1
        event = req["updates"][0]
        match event[0]:
            case 10004:
                raw_message = EventMessage(*event)
                if raw_message.chat_id == vk_chat_id:
                    message, profile = get_message(access_token, req["pts"]-1)
                    message = Message(**message[0], profiles=profile)
                    print(message)
        
    if req.get("failed", False) == 1:
        ts = req["ts"]
    elif req.get("failed", False) == 2:
        credentials = get_credentials(get_web_token(cookie))
        ts = credentials["ts"]
        key = credentials["key"]
        