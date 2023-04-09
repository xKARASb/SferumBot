import asyncio, os

from models.db import connect_db
from models.user import User
from functions.functions import message_text_validate

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

load_dotenv()

bot_token = os.getenv("BOT_TOKEN")


bot = Bot(bot_token)
dp = Dispatcher(bot)


def error_message_cookie_invalid(id, text):
    text = "Не удалось авторизоваться\! Обновите cookie в боте командой _/cookie set_"
    asyncio.run(bot.send_message(id, text, parse_mode="Markdownv2"))

def send_messages(id, sender, text):
    session = connect_db()
    chat_id = session.query(User).filter(User.id==id).first().chat_id
    session.close()
    text = message_text_validate(text)
    message = f"От {sender}: \n {text}"
    asyncio.run(bot.send_message(chat_id,  text=message))

def send_photo(id: int, photo_url: str, text = ''):
    session = connect_db()
    chat_id = session.query(User).filter(User.id==id).first().chat_id
    session.close()
    
    text = message_text_validate(text)
    message = f"{text}"
    
    asyncio.run(bot.send_photo(chat_id, photo=photo_url, caption=message))
