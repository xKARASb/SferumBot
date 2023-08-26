from os import getenv
from dotenv import load_dotenv

from aiogram.types import Message, PollAnswer
from aiogram import Dispatcher, F

from vk.methods import send_message, send_vote

load_dotenv()
host_id = getenv("TG_USER_ID")

dp = Dispatcher()

@dp.message(F.from_user.id==host_id)
async def on_message(message: Message) -> None:
    from main import bot
    send_message(bot.access_token, bot.peer_id, message.text)

@dp.poll_answer(F.from_user.id==host_id)
async def on_poll_answer(poll_answer: PollAnswer) -> None:
    from main import bot
    send_vote(poll_answer, bot.access_token)

async def start_polling(bot) -> None:
    await dp.start_polling(bot)