import requests

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