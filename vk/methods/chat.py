import requests

from vk.types import Profile

def get_members(access_token, peer) -> list[Profile] | None:
    data = {
        "access_token": access_token,
        "peer_id": peer,
        "extended": 1,
        "fields": ', '.join(["id", "first_name", "last_name"])
    }
    req = requests.post("https://api.vk.me/method/messages.getConversationMembers?v=5.218", data=data).json()
    if req.get("error"):
        return None
    return [Profile(**user) for user in req["response"]["profiles"]]