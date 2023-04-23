import os, asyncio, json, re

from multiprocessing import Process

from dotenv import load_dotenv

from functions.functions import (
    encrypt_cookie,
    chek_cookie,
    decrypt_cookie,
    message_text_validate
    )
from models.db import connect_db
from models.user import User


from browser.web_window import web_window

from aiogram import Bot, Dispatcher, Router, F

from aiogram.utils.keyboard import ReplyKeyboardBuilder

from aiogram.filters import Command, Filter, Text
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton,
    InlineQuery
)   

load_dotenv()

bot_token = os.getenv("BOT_TOKEN")
bot = Bot(bot_token, parse_mode="HTML")

router = Router()



@router.message(Command(commands=['start']))
async def send_start(msg: Message):

    button = KeyboardButton(text="/cookie")
    button2 = KeyboardButton(text="/sferum")
    button3 = KeyboardButton(text="/channel")
    keyboard_b = ReplyKeyboardBuilder([[button, button2, button3]])
    keyboard = keyboard_b.as_markup()
    #keyboard.add(button,button2, button3)
    keyboard.resize_keyboard = True
    text = """*Настройка бота:*
• /cookie \- инструкция для аунтификации бота в Сферуме
• /sferum \- инструкция для установки с какого чата брать сообщения в сферуме
• /channel \- инструкция как назначить канал сообщений из сферума
• /activate \- активация бота в первый раз\!
_рекомендуется настраивать с ПК, __т\.к с приложения ВК мессенджер__ *не получится\!*_"""
    await bot.send_message(msg.from_user.id, text, reply_markup=keyboard, parse_mode="MarkdownV2")

@router.message(Command(commands=["activate"]))
async def start_handling(msg: Message):
    session = connect_db()
    user = session.query(User).filter(User.id==msg.from_user.id).first()
    if user:
        peer = user.peer
        chat_id = user.chat_id
        cookie = user.cookie
        vk_id = user.vk_id

        if not cookie:
            await bot.send_message(msg.from_user.id, "Вы не установили cookie! Используйте /cookie для подробностей")
            return
        elif not chat_id:
            await bot.send_message(msg.from_user.id, "Вы не установили чат для сообщений! Используйте /chat_id для подробностей")
            return
        elif not peer:
            await bot.send_message(msg.from_user.id, "Вы не установили чат прослушки (peer)! Используйте /peer для подробностей")
            return
        else:
            with open("autoconnect/pool.json", "r") as f:
                data = json.load(f)
            if msg.from_user.id in data:
                await msg.reply("Бот уже активирован!")
                return
            
            cookie = decrypt_cookie(cookie)

            data.append(msg.from_user.id)
            #data[0].append([cookie, msg.from_user.id, peer, vk_id])
            with open("autoconnect/pool.json", "w") as f:
                json.dump(data, f)
            #Call web windown
            task = Process(target=web_window, args=(cookie, msg.from_user.id, peer, vk_id))
            task.start()
            pass

    else:
        await bot.send_message(msg.from_user.id, "Вы не настроили бота!")


@router.message(Command(commands=["cookie"]))
async def cookie(msg: Message):
    tokens = msg.text.split(" ")
    if tokens:
        match tokens[1]:
            case "set":
                if not len(tokens) == 3:
                    await bot.send_message(msg.from_user.id, "Вы не ввели cookie!", reply_markup=ReplyKeyboardRemove())
                    return
                cookie = tokens[2]
                vk_id = chek_cookie(cookie)
                if vk_id.get("error", False):
                    await bot.send_message(msg.from_user.id, "Cookie не корректен!")
                    return 
                
                session = connect_db()

                if not session.query(User).filter(User.id==msg.from_user.id).first():
                    db_cookie = encrypt_cookie(cookie)
                    session.add(User(msg.from_user.id, db_cookie, None, None, vk_id))
                    await bot.send_message(msg.from_user.id, "Аунтификация настроена!")
                else:
                    db_cookie = encrypt_cookie(cookie)
                    user = session.query(User).filter(User.id==msg.from_user.id).first()
                    user.cookie = db_cookie
                    user.vk_id = vk_id["id"]
                    await bot.send_message(msg.from_user.id, "Куки установлен!")

                session.commit()
                await bot.delete_message(msg.from_user.id, message_id=msg.message_id)
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
    

    await bot.send_message(msg.from_user.id, instruction, parse_mode="MarkdownV2", reply_markup=ReplyKeyboardRemove())
    await bot.send_photo(msg.from_user.id, "https://disk.yandex.com/i/BUDmx35VkXgRSw", parse_mode="MarkdownV2", reply_markup=ReplyKeyboardRemove())
        
@router.message(Command(commands=["sferum"]))
async def sferum(msg: Message):
    instruction = "Тебе нужно отправить ссылку на чат Сферума, из которого ты хочешь получать сообщения\!"
    await bot.send_message(msg.from_user.id, instruction, parse_mode="Markdownv2")

@router.message(F.text.regexp(r"https://web.vk.me/convo/(-?\d{9,10})").as_("peer"))#Можно было сделать спилитом, но так интеерснее Эта регулярка отедляет peer от остльного пути ссылки, позваляя нам спокойно получить peer - чат id в Сферуме
async def peer(msg:Message, peer):
    session = connect_db()
    if not session.query(User).filter(User.id==msg.from_user.id).first():
        session.add(User(msg.from_user.id, None, peer.group(1), None, None))
        await bot.send_message(msg.from_user.id, "Peer настроен!")
    else:
        user = session.query(User).filter(User.id==msg.from_user.id).first()
        user.peer = peer.group(1)
        await bot.send_message(msg.from_user.id, "Peer обновлён!")
    session.commit()
    session.close()

@router.message(Command(commands=["channel"]))
async def telegram(msg: Message):
    tokens = msg.text.split()
    print(msg.text, type(msg.text))
    print(tokens)
    if tokens:
        match tokens[1]:
            case "set":
                session = connect_db()
                if not session.query(User).filter(User.id==msg.from_user.id).first():
                    session.add(User(msg.from_user.id, None, None, msg.chat.id, None))
                else:
                    user = session.query(User).filter(User.id==msg.from_user.id).first()
                    user.chat_id = msg.chat.id
                session.commit()
                session.close()
                await bot.send_message(msg.chat.id, "Этот канал установлен для сообщений из Сферума!")
                return
    instruction = "Что бы установить канал, тебе нужно прописать команду _/channel set_, в нужном чате где есть бот\!"
    await bot.send_message(msg.chat.id, instruction, parse_mode="Markdownv2") 

@router.message(Command(commands=["test"]))
async def test(msg: Message):
    tokens = msg.text.split(" ")
    session = connect_db()
    chnl_id = session.query(User).filter(User.id == msg.from_user.id).first().chat_id
    await bot.send_message(chnl_id, tokens[1])


def start_bot():
#    executor.start_polling(dp, skip_updates=True)
    dp = Dispatcher()
    dp.include_router(router)

    asyncio.run(dp.start_polling(bot))
