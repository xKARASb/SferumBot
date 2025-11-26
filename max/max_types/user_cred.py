"""User credentials object for Max Messenger."""


class UserCredentials:
    """User credentials class for Max Messenger."""
    
    def __init__(self, **kwargs: dict) -> None:
        """Build user credentials."""
        self.__dict__.update(kwargs)
    
    user_id: int
    profile_type: int  # 1-female 2-male
    access_token: str
    expires: int