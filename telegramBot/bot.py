import os, asyncio
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
                    if session.query(exists().where(User.id == msg.from_id)).scalar():
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
    pass

async def send_vk_message():
    pass


def start_bot():
    executor.start_polling(dp, skip_updates=True)

    

#asyncio.run(bot.send_message(-1001917922644, "Пук"))