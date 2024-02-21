class ServerCredentials:
    server: str
    key: str
    ts: int
    pts: int

    def __init__(self, **kwargs) -> None:
        self.__dict__.update(kwargs)