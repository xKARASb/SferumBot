from models.create_db import create_db
from telegramBot.bot import start_bot
from browser.web_window import web_window
from threading import Thread


if __name__ == "__main__":
    #window = web_window("vk1.a.yQtWzxI9773GObEuQjqRztVnaE85uphrByMqTlVtMBhx8VIPjakWl5CAVUIrJawuO_8sOaycvIKVSQo8EXyeoKLQ2I5G1TCBbODwxJ5qoOly5lT8bZcrAmtXoe991W8LcDg9dUlliZEyqjxw8BtVzCQXla-9sii4DcwllSIrohU", 1810265462, 791592975, 791593813)

    create_db()
    start_bot()

    #asyncio.run(send_photo(-1001917922644, "https://sun9-35.userapi.com/impg/dtcSfuO-AJkXYckk4bXwlPB8W-Mmeok5xUy-Mg/kAkLZ_y_-P0.jpg?size=510x511&quality=95&sign=f843558b969b650f95c0b0bccbaf17a6&c_uniq_tag=kEInpB4XUGgLMaZn44Ugys8oLjVEeJY4WP5XRvtX3JA&type=album", "Брбрбрбр"))

    