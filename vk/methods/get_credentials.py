"""Get server info."""

import requests
from loguru import logger

from vk.types import ServerCredentials

from .consts import LP_VERSION, V


def get_credentials(access_token: str) -> ServerCredentials:
    """Get server info."""
    body = {
        "need_pts": 1,
        "group_id": 0,
        "LP_VERSION": LP_VERSION,
        "access_token": access_token,
    }

    query = {
        "v": V,
    }

    req = requests.post(
        "https://api.vk.me/method/messages.getLongPollServer",
        data=body,
        params=query,
        timeout=20,
    )

    # Print log
    logger.debug(req.json())

    return ServerCredentials(**req.json()["response"])
