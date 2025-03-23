"""Get server info."""

from aiohttp import ClientSession
from loguru import logger

from vk.vk_types import ServerCredentials

from .consts import LP_VERSION, V


async def get_credentials(
    access_token: str,
    session: ClientSession,
) -> ServerCredentials:
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

    async with session.post(
        "https://api.vk.me/method/messages.getLongPollServer",
        data=body,
        params=query,
    ) as r:
        req = await r.json()

    # Print log
    logger.debug(req)

    return ServerCredentials(**req["response"])
