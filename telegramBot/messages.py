import asyncio, os, requests

from models.db import connect_db
from models.user import User
from functions.functions import message_text_validate

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
#from aiogram.client.session.base import BaseSession 

from aiogram.types import (
    URLInputFile,
    BufferedInputFile,
    InputMediaPhoto,
    InputMediaAudio,
    InputMediaDocument
)

load_dotenv()

bot_token = os.getenv("BOT_TOKEN")

def bot_insts():
    bot = Bot(bot_token)
    return bot
#dp = Dispatcher()


def error_message_cookie_invalid(id, text):
    text = "Не удалось авторизоваться\! Обновите cookie в боте командой _/cookie set_"
    bot = bot_insts()
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
#    bot_session = BaseSession()
#    bot_session.make_request(bot, SendMessage)
    bot = bot_insts()
    asyncio.run(bot.send_message(chat_id,  text=message, parse_mode="Markdownv2"))


def send_media(id: int, media_url: tuple[tuple()]):
    session = connect_db()
    chat_id = session.query(User).filter(User.id==id).first().chat_id
    session.close()
    
    media = []
    docs = []
    for url in media_url:
        match url[0]:
            case "photo":
                media.append(InputMediaPhoto(media=url[1]))
            case "doc":
                resp = requests.get(url[1], allow_redirects=False)
                resp = requests.get(resp.headers["Location"])
                document = BufferedInputFile(resp.content, filename=url[2])
                doc = InputMediaDocument(media=document)
                docs.append(doc)
            case "audio":
                media.append(InputMediaAudio(media=url[1]))
    
    if docs:
        bot = bot_insts()
        asyncio.run(bot.send_media_group(chat_id, media=docs, disable_notification=True))
    if media:
        bot = bot_insts()
        asyncio.run(bot.send_media_group(chat_id, media=media, disable_notification=True))
        

def send_doc(id: int, doc_title, doc_url):
    session = connect_db()
    chat_id = session.query(User).filter(User.id==id).first().chat_id
    session.close()
    resp = requests.get(doc_url, allow_redirects=False)
    resp = requests.get(resp.headers["Location"])
    document = BufferedInputFile(resp.content, filename=doc_title)
    bot = bot_insts()
    asyncio.run(bot.send_document(chat_id, document=document, disable_notification=True)) 

def send_photo(id: int, sender,  photo_url: str) -> None:
    session = connect_db()
    chat_id = session.query(User).filter(User.id==id).first().chat_id
    session.close()

    bot = bot_insts()
    asyncio.run(bot.send_photo(chat_id, photo=photo_url, disable_notification=True))
