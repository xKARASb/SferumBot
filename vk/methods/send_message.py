"""Send msg."""

from random import randint

import requests

from .consts import V


def send_message(access_token: str, peer_id: int, text: str) -> None:
    """Send msg."""
    data = {
        "access_token": access_token,
        "peer_id": peer_id,
        "random_id": -randint(100000000, 999999999),
        "message": text,
    }

    query = {
        "v": V,
    }

    requests.post(
        "https://api.vk.me/method/messages.send",
        data=data,
        params=query,
        timeout=20,
    )
