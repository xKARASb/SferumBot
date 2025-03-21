"""Bot startup module."""

import asyncio
import sys
from os import getenv

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import ClientSession
from dotenv import load_dotenv
from loguru import logger

from main import main as _main
from vk.methods import get_credentials, get_user_credentials

# Get and check the consts from .env
load_dotenv()

AUTH_COOKIE = getenv("AUTH_COOKIE")
if not AUTH_COOKIE:
    logger.error("Необходимо заполнить AUTH_COOKIE в .env")
    sys.exit()

BOT_TOKEN = getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("Необходимо заполнить BOT_TOKEN в .env")
    sys.exit()

TG_CHAT_ID = getenv("TG_CHAT_ID")
if not TG_CHAT_ID:
    TG_CHAT_ID = getenv("TG_USER_ID")
    if not TG_CHAT_ID:
        logger.error("Необходимо заполнить TG_USER_ID в .env")
        sys.exit()

VK_CHAT_ID = getenv("VK_CHAT_ID")
if not VK_CHAT_ID:
    logger.error("Необходимо заполнить VK_CHAT_ID в .env")
    sys.exit()


async def main() -> None:
    """Bot startup function."""
    # Connect logs file
    logger.add("sferum.log")

    try:
        # Creating an aiogram seesion object
        async with ClientSession() as session:

            # Any data
            user = await get_user_credentials(AUTH_COOKIE, session)
            access_token = user.access_token
            creds = await get_credentials(access_token, session)

            # Initializing bot
            bot = Bot(
                BOT_TOKEN,
                default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2),
            )

            # Print the log
            logger.info("Bot was started")

            # Run the main cycle
            await _main(
                session,
                creds.server, creds.key, creds.ts,
                TG_CHAT_ID, VK_CHAT_ID, access_token,
                AUTH_COOKIE, creds.pts, bot,
            )

    except KeyboardInterrupt:
        logger.info("Bot was stoped")
        await bot.close()

    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    asyncio.run(main())
