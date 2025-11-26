"""Max API constants."""

# Max API version (based on PyMax)
V = "5.199"

# LongPoll version
LP_VERSION = 3

# Max API endpoints (based on PyMax)
MAX_API_BASE = "https://api.vk.com"
MAX_WEB_BASE = "https://web.vk.me"

# API methods (based on PyMax)
METHODS = {
    "get_long_poll_server": "messages.getLongPollServer",
    "get_long_poll_history": "messages.getLongPollHistory",
    "get_history": "messages.getHistory",
    "get_user": "users.get",
    "send_message": "messages.send",
}