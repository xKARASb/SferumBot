from aiogram.types import Message
from aiogram import Dispatcher
from vk.methods import send_message

dp = Dispatcher()

@dp.message()
async def on_message(message: Message) -> None:
    from main import bot
    send_message(bot.access_token, bot.peer_id, message.text)

async def start_polling(bot) -> None:
    await dp.start_polling(bot)