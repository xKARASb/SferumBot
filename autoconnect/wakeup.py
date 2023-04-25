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
            tg_id = user.id
            peer = user.peer
            chat_id = user.chat_id
            cookie = user.cookie
            vk_id = user.vk_id
            
            cookie = decrypt_cookie(cookie)
            task = Process(target=web_window, args=(cookie, tg_id, peer, vk_id))
            task.daemon = True
            task.start()
            with open("autoconnect/active_pool.json", "r") as f:
                data = json.load(f)
            data.update({int(tg_id):task.pid})
            with open("autoconnect/active_pool.json", "w") as f:
                json.dump(data, f)
            logging.info(f"NEW WINDOW pid: {task.pid}")
    #with Pool(len(users_pool[0])+1) as pool:
    #    pool.starmap(web_window, users_pool[0])
        