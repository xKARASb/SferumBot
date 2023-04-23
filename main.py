from models.create_db import create_db
from telegramBot.bot import start_bot
from autoconnect.wakeup import wake_up
#from multiprocessing import Process
import logging


if __name__ == "__main__":
    create_db()
    logging.info("Подключение пользователей...")
    #task = Process(target=wake_up)
    #task.start()
    wake_up()
    logging.info("Подключение бота...")
    start_bot()