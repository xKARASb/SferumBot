from .consts import v
import requests
import logging


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
    logging.debug(f"[VK API] get_message response: {req}")
    if req.get("error"):
        return {"error": True, "text": "access token has expired"}
    
    peer_type = req["response"]["conversations"][-1]["peer"]["type"]

    if peer_type == "user":
        title = "Direct message"
    elif peer_type == "chat":
        title = req["response"]["conversations"][-1]["chat_settings"]["title"]
    else:
        title = "None"

    return {
        "items": req["response"]["messages"]["items"],
        "profiles": req["response"]["profiles"],
        "title": title
        }
