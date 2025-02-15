"""Get history."""

import requests
from loguru import logger

from .consts import LP_VERSION, V


def get_history(access_token: str, ts: int, pts: int) -> tuple:
    """Get history."""
    body = {
        "access_token": access_token,
        "ts": ts,
        "pts": pts,
        "fields": "id,first_name,last_name",
        "LP_VERSION": LP_VERSION,
        "last_n": 1,
        "extended": 1,
        "credentials": 1,
    }

    query = {
        "v": V ,
    }

    req = requests.post(
        "https://api.vk.me/method/messages.getLongPollHistory",
        params=query,
        data=body,
        timeout=20,
    ).json()

    logger.debug(req)

    if req.get("error"):
        return {"error": True, "message": "Access token expired"}
    return req["response"]["messages"]["items"], req["response"]["profiles"],\
            req["response"]["conversations"][-1]["chat_settings"]["title"]
