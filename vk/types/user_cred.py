class UserCredentials:
    user_id: int
    profile_type: int # 1-female 2-male
    access_token: str
    expires: int

    def __init__(self, **kwargs) -> None:
        self.__dict__.update(kwargs)