import os, asyncio, re
from dotenv import load_dotenv
from sqlalchemy.sql import exists

from functions import encrypt_cookie
from models.db import connect_db
from models.user import User


from aiogram import Bot, Dispatcher, executor
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineQuery
)   

load_dotenv()

bot_token = os.getenv("BOT_TOKEN")


bot = Bot(bot_token)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_start(msg: Message):

    keyboard = ReplyKeyboardMarkup(3, resize_keyboard=True)
    button = InlineKeyboardButton("/cookie")
    button2 = InlineKeyboardButton("/sferum")
    button3 = InlineKeyboardButton("/channel")
    keyboard.add(button,button2, button3)
    text = """*Настройка бота:*
• /cookie \- инструкция для аунтификации бота в Сферуме
• /sferum \- инструкция для установки с какого чата брать сообщения в сферуме
• /channel \- инструкция как назначить канал сообщений из сферума
_рекомендуется настраивать с ПК, __т\.к с приложения ВК мессенджер__ *не получится\!*_"""
    print(msg.get_args())
    await bot.send_message(msg.from_id, text, reply_markup=keyboard, parse_mode="MarkdownV2")


@dp.message_handler(commands=["cookie"])
async def cookie(msg: Message):
    tokens = msg.get_args().split(" ")
    if tokens:
        match tokens[0]:
            case "set":
                if len(tokens) == 2:
                    cookie = tokens[1]
                    db_cookie = encrypt_cookie(cookie)
                    session = connect_db()
                    if not session.query(User).filter(User.id==msg.from_id).first():
                        session.add(User(msg.from_id, db_cookie, None, None))
                        await bot.send_message(msg.from_id, "Аунтификация настроена!")
                    else:
                        user = session.query(User).filter(User.id==msg.from_id).first()
                        user.cookie = db_cookie
                        await bot.send_message(msg.from_id, "Куки обновлён!")
                    session.commit()
                    session.close()
                    await bot.delete_message(msg.from_id, message_id=msg.message_id)
                    return
                else:
                    await bot.send_message(msg.from_id, "Вы не ввели cookie!", reply_markup=ReplyKeyboardRemove())
                    return
            case _:
                pass
    instruction = """__Для чего нужен cookie файл?__
*Cookie файл требуется*, для аунтификации бота в Сферуме, под вашим аккаунтом\.
_\!\!\!Важно бот получит доступ только к аккаунту Сферума, все cookie файлы хранятся в шифровоном виде надёжно\!\!\!_ 
__Инструкция как получить нужный cookie файл__:
  *1\.* Зайдите в удобный Вам браузер \(кроме Google Chrome\) и откройте [Сферум](https://web.vk.me) если не обходимо, зайдите в аккаунт\.
  *2\.* Как вы попали на главную страницу, следуйте инструкции на фотографии и скопируйте "Контент"\("Value"\)\.
  *3\.* После того, как вы скопировали cookie с имнем _remixdsid_, введите команду _/cookie set \<ваш куки\>_"""
    

    await bot.send_message(msg.from_id, instruction, parse_mode="MarkdownV2", reply_markup=ReplyKeyboardRemove())
    await bot.send_photo(msg.from_id, "https://disk.yandex.com/i/BUDmx35VkXgRSw", parse_mode="MarkdownV2", reply_markup=ReplyKeyboardRemove())
        
@dp.message_handler(commands=["sferum"])
async def sferum(msg: Message):
    tokens = msg.get_args().split(" ")
    if tokens:
        match tokens[0]:
            case "set":
                if len(tokens) == 2:

                    peer = tokens[1]
                    pattern = re.compile(r"(https://web.vk.me/#/convo/)(-?\d{9,10})") #Можно было сделать спилитом, но так интеерснее Эта регулярка отедляет peer от остльного пути, позваляя нам спокойно получить peer - чат id в Сферуме
                    peer = pattern.match(peer).group(2)
                    session = connect_db()
                    if not session.query(User).filter(User.id==msg.from_id).first():
                        session.add(User(msg.from_id, None, peer, None))
                        await bot.send_message(msg.from_id, "Peer настроен!")
                    else:
                        user = session.query(User).filter(User.id==msg.from_id).first()
                        user.peer = peer
                        await bot.send_message(msg.from_id, "Peer обновлён!")
                    session.commit()
                    session.close()
                    return
                else:
                    await bot.send_message(msg.from_id, "Peer не корректен!", reply_markup=ReplyKeyboardRemove())
                    return
            case _:
                pass
    instruction = "Тебе нужно отправить ссылку на чат в комманде _/sferum set \<ссылка\>_, из которого ты хочешь получать сообщения в Сферуме\!"
    await bot.send_message(msg.from_id, instruction, parse_mode="Markdownv2")

@dp.message_handler(commands=["channel"])
async def telegram(msg: Message):
    tokens = msg.get_args().split(" ")
    if tokens:
        match tokens[0]:
            case "set":
                session = connect_db()
                if not session.query(User).filter(User.id==msg.from_id).first():
                    session.add(User(msg.from_id, None, None, msg.chat.id))
                else:
                    user = session.query(User).filter(User.id==msg.from_id).first()
                    user.chat_id = msg.chat.id
                session.commit()
                session.close()
                await bot.send_message(msg.chat.id, "Этот канал установлен для сообщений из Сферума!")
                return
    instruction = "Что бы установить канал, тебе нужно прописать команду /channel set, в нужном чате где есть бот!"
    await bot.send_message(msg.chat.id, instruction)

@dp.message_handler(commands=["test"])
async def test(msg: Message):
    tokens = msg.get_args().split(" ")
    session = connect_db()
    chnl_id = session.query(User).filter(User.id == msg.from_id).first().chat_id
    await bot.send_message(chnl_id, tokens[0])

async def send_vk_message():
    session = connect_db()
#    chnl_id = session.query(User).filter(User.id == msg.from_id).first().chat_id


def start_bot():
    executor.start_polling(dp, skip_updates=True)

