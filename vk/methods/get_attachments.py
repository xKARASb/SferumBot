import requests
from .consts import v


def get_attachments(access_token, pts):
    body = {
        "extended": 1,
        "pts": pts,
        "fields":"id,first_name,last_name",
        "access_token": access_token
    }

    query = {
        "v": v
    }

    req = requests.post("https://api.vk.me/method/messages.getLongPollHistory",
                        data=body, params=query).json()
    
    if req["response"]["messages"].get("items"):
        req = req["response"]["messages"]["items"][-1]
    return (req["attachments"],\
            req["fwd_messages"])
