"""Bot main module."""

import sys
from os import getenv

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from dotenv import load_dotenv
from loguru import logger

from vk.methods import send_message

# Get and check the consts from .env
load_dotenv()

TG_USER_ID = getenv("TG_USER_ID")
if not TG_USER_ID:
    logger.error("Необходимо заполнить TG_USER_ID в .env")
    sys.exit()

# Initializing dispatcher
dp = Dispatcher()

@dp.message(F.from_user.id == TG_USER_ID)
async def on_message(message: Message, bot: Bot) -> None:
    """Send message."""
    send_message(bot.peer_id, message.text)
    print(message.text)

async def start_polling(bot: Bot) -> None:
    """Start polling function."""
    await dp.start_polling(bot)
