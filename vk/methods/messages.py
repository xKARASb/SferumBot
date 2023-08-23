import requests
from random import randint

def get_attachments(access_token, pts) -> list:
    body = {
        "extended": 1,
        "pts": pts,
        "fields":"id,first_name,last_name",
        "access_token": access_token
    }
    req = requests.post("https://api.vk.me/method/messages.getLongPollHistory?v=5.217", data=body).json()
    return (req["response"]["messages"]["items"][0]["attachments"], req["response"]["messages"]["items"][0]["fwd_messages"])

def get_message(access_token, pts) -> tuple[list, list]:
    body = {
        "extended": 1,
        "pts": pts,
        "fields":"id,first_name,last_name",
        "access_token": access_token
    }
    req = requests.post("https://api.vk.me/method/messages.getLongPollHistory?v=5.217", data=body).json()
    return req["response"]["messages"]["items"], req["response"]["profiles"]

def send_message(access_token, peer_id, msg) -> None:
    data = {
        "access_token": access_token,
        "peer_id": peer_id,
        "random_id": -randint(100000000, 999999999),
        "message": msg
    }
    requests.post("https://api.vk.me/method/messages.send?v=5.218", data=data)