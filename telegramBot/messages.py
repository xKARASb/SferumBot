import asyncio, os

from models.db import connect_db
from models.user import User
from functions.functions import message_text_validate

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from aiogram.types import (
    MediaGroup,
    InputFile
)

load_dotenv()

bot_token = os.getenv("BOT_TOKEN")


bot = Bot(bot_token)
dp = Dispatcher(bot)


def error_message_cookie_invalid(id, text):
    text = "Не удалось авторизоваться\! Обновите cookie в боте командой _/cookie set_"
    asyncio.run(bot.send_message(id, text, parse_mode="Markdownv2"))

def send_messages(id, sender, text, urls = False):
    session = connect_db()
    chat_id = session.query(User).filter(User.id==id).first().chat_id
    session.close()
    text = message_text_validate(text)
    message = f"От {sender}: \n {text}"
    if urls:
        message = f"{message}\n Ссылки: {urls}"
    print(message)
    asyncio.run(bot.send_message(chat_id,  text=message, parse_mode="Markdownv2"))


def send_media(id: int, media_url: tuple[tuple()]):
    session = connect_db()
    chat_id = session.query(User).filter(User.id==id).first().chat_id
    session.close()
    
    media = MediaGroup()

    for url in media_url:
        match url[0]:
            case "photo":
                media.attach_photo(url[1],)
            case "video":
                print(url[1])
                media.attach_video(url[1])
            case "doc":
                media.attach_document(url[1])
            case "audio":
                media.attach_audio(url[1])
    
    asyncio.run(bot.send_media_group(chat_id, media=media))

def send_photo(id: int, sender,  photo_url: str) -> None:
    session = connect_db()
    chat_id = session.query(User).filter(User.id==id).first().chat_id
    session.close()

    asyncio.run(bot.send_photo(chat_id, photo=photo_url,))
