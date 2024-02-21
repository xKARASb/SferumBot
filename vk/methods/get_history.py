import requests
from .consts import v, lp_version


def get_history(access_token, ts, pts):
    body = {
        "access_token": access_token,
        "ts": ts,
        "pts": pts,
        "fields": "id,first_name,last_name",
        "lp_version": lp_version,
        "last_n": 1,
        "extended": 1,
        "credentials": 1
    }

    query = {
        "v": v 
    }

    req = requests.post("https://api.vk.me/method/messages.getLongPollHistory",
                        params=query, data=body).json()


    if req.get("error"):
        return {"error": True, "message": "Access token expired"}
    return req["response"]["messages"]["items"], req["response"]["profiles"],\
            req["response"]["conversations"][-1]["chat_settings"]["title"]
