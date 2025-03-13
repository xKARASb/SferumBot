"""Server info object."""


class ServerCredentials:
    """Server info class."""

    server: str
    key: str
    ts: int
    pts: int

    def __init__(self, **kwargs: dict) -> None:
        """Server info class builder."""
        self.__dict__.update(kwargs)
