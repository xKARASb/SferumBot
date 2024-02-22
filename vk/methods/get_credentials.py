import requests
from .consts import v, lp_version
from vk.types import ServerCredentials


def get_credentials(access_token) -> ServerCredentials:
    body = {
        "need_pts": 1,
        "group_id": 0,
        "lp_version": lp_version,
        "access_token": access_token
    }

    query = {
        "v": v
    }

    req = requests.post("https://api.vk.me/method/messages.getLongPollServer",
                        data=body, params=query)
    
    return ServerCredentials(**req.json()["response"])
