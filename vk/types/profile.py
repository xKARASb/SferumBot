class Profile:
    id: int
    first_name: str
    last_name: str

    def __init__(self, **kwargs) -> None:
        self.__dict__.update(kwargs)
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"