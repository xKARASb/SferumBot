# FIXME(@iamlostshe): /home/<full_path>/startup.py:32: DeprecationWarning: There is no current event loop
# loop = asyncio.get_event_loop()
#
# Я понимаю, что это всего лишь предупреждение, но его нужно ликвидировать.

import asyncio
from os import getenv

from aiogram import Bot
from dotenv import load_dotenv
from loguru import logger

from main import main as _main
from vk.methods import get_credentials, get_user_credentials

# Get the consts from .env
load_dotenv()

AUTH_COOKIE = getenv("AUTH_COOKIE")
BOT_TOKEN = getenv("BOT_TOKEN")
TG_CHAT_ID = getenv("TG_CHAT_ID")
VK_CHAT_ID = getenv("VK_CHAT_ID")


def main():
    # Connect logs file
    logger.add("sferum.log")

    # Any data
    user = get_user_credentials(AUTH_COOKIE)
    access_token = user.access_token
    creds = get_credentials(access_token)

    loop = asyncio.get_event_loop()

    try:
        bot = Bot(BOT_TOKEN)
        loop.create_task(_main(creds.server, creds.key, creds.ts, TG_CHAT_ID, VK_CHAT_ID, access_token, AUTH_COOKIE, creds.pts, bot, TG_TOPIC_ID))
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
