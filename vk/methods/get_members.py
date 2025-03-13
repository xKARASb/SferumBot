"""Get members."""

from __future__ import annotations

import requests
from loguru import logger

from .consts import V


def get_members(access_token: str, peer: int) -> dict | str:
    """Get members."""
    data = {
        "access_token": access_token,
        "peer_id": peer,
        "extended": 1,
        "fields": "id, first_name, last_name",
    }

    query = {
        "v": V,
    }

    req = requests.post(
        "https://api.vk.me/method/messages.getConversationMembers",
        data=data,
        params=query,
        timeout=20,
    ).json()

    logger.debug(req)

    if req.get("error"):
        return {"error": True, "text": "No profiles"}
    return req["response"]["profiles"]
