import os, asyncio
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, executor, types

load_dotenv()

bot_token = os.getenv("BOT_TOKEN")


bot = Bot(bot_token)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_start(msg: types.Message):
    await msg.reply("It`s me Mario!")

async def send_vk_message():
    pass


def start_bot():
    executor.start_polling(dp, skip_updates=True)

#asyncio.run(bot.send_message(-1001917922644, "Пук"))