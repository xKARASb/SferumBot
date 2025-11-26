"""Get info about user for Max Messenger."""

from aiohttp import ClientSession
from loguru import logger

from max.max_types import UserCredentials


async def get_user_credentials(
    auth_cookie: str,
    session: ClientSession,
) -> UserCredentials:
    """Get info about user from Max Messenger using PyMax approach."""
    cookies = {
        "remixdsid": auth_cookie,  # VK-style cookie for Max (based on PyMax)
    }

    query = {
        "act": "web_token",
        "app_id": 8202606,  # PyMax app_id
    }

    # Send request to Max web interface (using VK endpoints as PyMax does)
    async with session.get(
        "https://web.vk.me/",
        params=query,
        cookies=cookies,
        allow_redirects=False,
    ) as r:
        req = await r.json()

    # Print log
    logger.debug(req)

    # PyMax returns user data in different format, adapt as needed
    if req and len(req) > 1:
        return UserCredentials(**req[1])
    else:
        # Fallback for different response format
        return UserCredentials(
            user_id=0,
            profile_type=0,
            access_token="",
            expires=0
        )