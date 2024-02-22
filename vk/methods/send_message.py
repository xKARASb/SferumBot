import requests
from random import randint
from .consts import v


def send_message(access_token, peer_id, text) -> None:
    data = {
        "access_token": access_token,
        "peer_id": peer_id,
        "random_id": -randint(100000000, 999999999),
        "message": text
    }

    query = {
        "v": v 
    }

    requests.post("https://api.vk.me/method/messages.send",
                    data=data, params=query)