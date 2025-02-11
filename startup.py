# FIXME(@iamlostshe): /home/<full_path>/startup.py:32: DeprecationWarning: There is no current event loop
# loop = asyncio.get_event_loop()
#
# Я понимаю, что это всего лишь предупреждение, но его нужно ликвидировать.

import asyncio
from loguru import logger

from os import getenv
from dotenv import load_dotenv

from aiogram import Bot

from vk.methods import get_credentials, get_user_credentials

from main import main


# Connect logs file
logger.add("sferum.log")


load_dotenv()

tg_chat_id = getenv("TG_CHAT_ID")

# FIXME(@iamlostshe): Если значение не указано вызывает исключение:
#
# TypeError: int() argument must be a string, a bytes-like object or a real number, not 'NoneType'

tg_topic_id = int(getenv("TG_TOPIC_ID", default=0))
vk_chat_ids = getenv("VK_CHAT_ID")
bot_token = getenv("BOT_TOKEN")
cookie = getenv("AUTH_COOKIE")

user = get_user_credentials(cookie)
access_token = user.access_token
creds = get_credentials(access_token)

loop = asyncio.get_event_loop()

try:
    bot = Bot(bot_token)
    task2 = loop.create_task(main(creds.server, creds.key, creds.ts, tg_chat_id, vk_chat_ids, access_token, cookie, creds.pts, bot, tg_topic_id))
    logger.info("Loop starting")
    loop.run_forever()
except KeyboardInterrupt:
    pass
except Exception as e:
    logger.exception(e)
finally:
    logger.info("Closing loop...")
    loop.close()
    logger.info("Loop closed")