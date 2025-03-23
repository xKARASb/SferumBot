"""Bot main module."""

import sys
from os import getenv

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from loguru import logger

# Get and check the consts from .env
load_dotenv()

TG_USER_ID = getenv("TG_USER_ID")
if not TG_USER_ID:
    logger.error("Необходимо заполнить TG_USER_ID в .env")
    sys.exit()

# Initializing dispatcher
dp = Dispatcher()

async def start_polling(bot: Bot) -> None:
    """Start polling function."""
    await dp.start_polling(bot)
