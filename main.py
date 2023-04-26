from models.create_db import create_db
from telegramBot.bot import start_bot
from autoconnect.wakeup import wake_up
#from multiprocessing import Process
import logging
from dotenv import load_dotenv



if __name__ == "__main__":
    logging.basicConfig(encoding='utf-8', level=logging.INFO) #filename='logs/info.log', 

    load_dotenv()
    create_db()

    logging.info('\n'*15 + "New session")
    logging.info("Connection to VK")

    wake_up()
    logging.info("TG bot connect")
    start_bot()