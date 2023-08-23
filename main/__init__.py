import asyncio
from concurrent.futures import ProcessPoolExecutor

from os import getenv
from dotenv import load_dotenv

from aiogram import Bot

from vk.methods import get_credentials, get_web_token

from .main import main
from tgBot import start_polling

load_dotenv()

tg_chat_id = getenv("TG_CHAT_ID")
vk_chat_id = int(getenv("VK_CHAT_ID"))
bot_token = getenv("BOT_TOKEN")
cookie = getenv("AUTH_COOKIE")

access_token = get_web_token(cookie)
credentials = get_credentials(access_token)

ts = credentials["ts"]
key = credentials["key"]

loop = asyncio.get_event_loop()

try:
    bot = Bot(bot_token)
    bot.chat_id = tg_chat_id
    bot.access_token = access_token
    bot.peer_id = vk_chat_id
    task1 = loop.create_task(start_polling(bot))
    task2 = loop.create_task(main(key, ts, vk_chat_id, access_token, cookie, bot))
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    print("Closing Loop")
    loop.close()