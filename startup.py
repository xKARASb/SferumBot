import asyncio
import logging

from os import getenv
from dotenv import load_dotenv

from aiogram import Bot

from vk.methods import get_credentials, get_user_credentials

from main import main

load_dotenv()

logging.basicConfig(filename="../sferum_in.log", encoding="utf-8", level=logging.INFO, datefmt='%m/%d/%Y %I:%M:%S %p')

tg_chat_id = getenv("TG_CHAT_ID")
vk_chat_ids = getenv("VK_CHAT_ID")
bot_token = getenv("BOT_TOKEN")
cookie = getenv("AUTH_COOKIE")

user = get_user_credentials(cookie)
access_token = user.access_token
creds = get_credentials(access_token)

loop = asyncio.get_event_loop()

try:
    bot = Bot(bot_token)
    task2 = loop.create_task(main(creds.server, creds.key, creds.ts, tg_chat_id, vk_chat_ids, access_token, cookie, creds.pts, bot))
    logging.info("Loop starting")
    loop.run_forever()
except KeyboardInterrupt:
    pass
except Exception as e:
    logging.exception(e)
finally:
    logging.info("Closing loop...")
    loop.close()
    logging.info("Loop closed")