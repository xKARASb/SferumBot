"""Get info about user."""

import requests
from loguru import logger

from vk.types import UserCredentials


def get_user_credentials(auth_cookie: str) -> UserCredentials:
    """Get info about user."""
    cookies = {
        "remixdsid": auth_cookie,
    }

    query = {
        "act": "web_token",
        "app_id": 8202606,
    }

    # Send the request
    req = requests.get(
        "https://web.vk.me/",
        params=query,
        cookies=cookies,
        allow_redirects=False,
        timeout=20,
    )

    # Print log
    logger.debug(req.json())

    return UserCredentials(**req.json()[1])
