import json, logging

from browser.web_window import web_window
from models.user import User
from models.db import connect_db
from multiprocessing import Pool, Process
from functions.functions import decrypt_cookie

def wake_up():
    with open("autoconnect/pool.json") as f:
        users_pool = json.load(f)
    session = connect_db()
    for user in users_pool:
        user = session.query(User).filter(User.id==user).first()
        if user:
            task = start_window(user.id, user.peer, user.chat_id, user.cookie, user.vk_id)
            logging.info(f"AUTOCONNECT WINDOW pid: {task}")


def start_window(tg_id, peer, chat_id, cookie, vk_id, handl = None):           
    cookie = decrypt_cookie(cookie)
    task = Process(target=web_window, args=(cookie, tg_id, peer, vk_id, handl))
    task.start()
    with open("autoconnect/active_pool.json", "r") as f:
        data = json.load(f)
    data.update({int(tg_id):task.pid})
    with open("autoconnect/active_pool.json", "w") as f:
        json.dump(data, f)
    return task.pid
        