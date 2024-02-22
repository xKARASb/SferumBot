from .consts import v
import requests


def get_message(access_token, pts) -> tuple[list, list, str]:
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
    if req.get("error"):
        return {"error": True, "text": "access token has expired"}
    return req["response"]["messages"]["items"], req["response"]["profiles"],\
            req["response"]["conversations"][-1]["chat_settings"]["title"]
