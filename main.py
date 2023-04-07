from models.create_db import create_db
from telegramBot.bot import start_bot


if __name__ == "__main__":
    create_db()
    start_bot()

    