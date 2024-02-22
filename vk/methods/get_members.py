import requests
from .consts import v


def get_members(access_token, peer):
    data = {
        "access_token": access_token,
        "peer_id": peer,
        "extended": 1,
        "fields": 'id, first_name, last_name'
    }

    query = {
        "v": v
    }

    req = requests.post("https://api.vk.me/method/messages.getConversationMembers",
                        data=data, params=query).json()
    
    if req.get("error"):
        return {"error": True, "text": "No profiles"}
    return req["response"]["profiles"]