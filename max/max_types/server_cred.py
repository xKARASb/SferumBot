"""Server credentials object for Max Messenger."""


class ServerCredentials:
    """Server credentials class for Max Messenger."""
    
    def __init__(self, **kwargs: dict) -> None:
        """Build server credentials."""
        self.__dict__.update(kwargs)
    
    server: str
    key: str
    ts: int
    pts: int