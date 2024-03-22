import logging
import requests

from asyncio import sleep

from vk.methods import get_credentials, get_user_credentials, get_message
from tg.methods import send_message
from vk.types import Message, EventMessage

async def main(server, key, ts, tg_chat_id, vk_chat_ids, access_token, cookie, pts, bot):
    data = {
        "act": "a_check",
        "key": key,
        "ts": ts,
        "wait": 10  
    }
    while True:
        await sleep(.1)
        try:
            req = requests.post(f"https://{server}", data=data).json()
            
            if req.get("updates"):
                data["ts"] += 1
                event = req["updates"][0]

                if event[0] == 4:
                    raw_msg = EventMessage(*event)
                    logging.info(f"[MAIN] raw_msg: {raw_msg}")
                    if str(raw_msg.chat_id) in vk_chat_ids.split(", "):
                        # message, profile, chat_title = get_message(access_token, pts)
                        logging.debug("[MAIN] allowed chat")
                        
                        message = get_message(access_token, pts)
                        logging.info(message)

                        if message.get("error"):
                            access_token = get_user_credentials(cookie).access_token
                            credentials = get_credentials(access_token)
                            data["ts"] = credentials.ts
                            data["key"] = credentials.key                            
                            
                            message = get_message(access_token, pts)
                            logging.info(message)
                            
                        pts += 1
                        
                        message, profile, chat_title = message["items"], message["profiles"], message["title"]
    
                        msg = Message(**message[-1], profiles=profile, chat_title=chat_title)
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
            logging.exception(e)

