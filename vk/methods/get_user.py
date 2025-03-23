"""Get info about user."""

from aiohttp import ClientSession
from loguru import logger

from vk.vk_types import UserCredentials


async def get_user_credentials(
    auth_cookie: str,
    session: ClientSession,
) -> UserCredentials:
    """Get info about user."""
    cookies = {
        "remixdsid": auth_cookie,
    }

    query = {
        "act": "web_token",
        "app_id": 8202606,
    }

    # Send the request
    async with session.get(
        "https://web.vk.me/",
        params=query,
        cookies=cookies,
        allow_redirects=False,
    ) as r:
        req = await r.json()

    # Print log
    logger.debug(req)

    return UserCredentials(**req[1])
