import requests

from .consts import V


def get_attachments(access_token, pts):
    body = {
        "extended": 1,
        "pts": pts,
        "fields":"id,first_name,last_name",
        "access_token": access_token,
    }

    query = {
        "v": V,
    }

    req = requests.post(
        "https://api.vk.me/method/messages.getLongPollHistory",
        data=body,
        params=query,
        timeout=20,
    ).json()

    if req["response"]["messages"].get("items"):
        req = req["response"]["messages"]["items"][-1]
    return (req["attachments"],\
            req["fwd_messages"])
