"""Bot startup module."""

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


async def main() -> None:
    """Bot startup function."""
    # Connect logs file
    logger.add("sferum.log")

    # Any data
    user = get_user_credentials(AUTH_COOKIE)
    access_token = user.access_token
    creds = get_credentials(access_token)

    try:
        # Initializing bot
        bot = Bot(BOT_TOKEN)

        # Print the log
        logger.info("Bot was started")

        # Run the main cycle
        await _main(
            creds.server, creds.key, creds.ts,
            TG_CHAT_ID, VK_CHAT_ID, access_token,
            AUTH_COOKIE, creds.pts, bot,
        )

    except KeyboardInterrupt:
        logger.info("Bot was stoped")

    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    asyncio.run(main())
