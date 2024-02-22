from os import getenv
from dotenv import load_dotenv

from aiogram.types import Message, PollAnswer
from aiogram import Dispatcher, F, Bot

from vk.methods import send_message

load_dotenv()
host_id = int(getenv("TG_USER_ID"))

dp = Dispatcher()

@dp.message(F.from_user.id==host_id)
async def on_message(message: Message, bot: Bot) -> None:
    send_message(bot.peer_id, message.text)

async def start_polling(bot) -> None:
    await dp.start_polling(bot)