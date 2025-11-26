"""Max API methods module."""

from .get_credentials import get_credentials
from .get_message import get_message
from .get_user import get_user_credentials
from .get_user_credentials import get_user_credentials as get_user_credentials_alt

__all__ = ['get_credentials', 'get_message', 'get_user_credentials', 'get_user_credentials_alt']