"""User profile object."""


class Profile:
    """User profile class."""

    id: int
    first_name: str
    last_name: str

    def __init__(self, **kwargs: dict) -> None:
        """Build user profile."""
        self.__dict__.update(kwargs)

    async def get_full_name(self) -> str:
        """Return user fullname."""
        return f"{self.first_name} {self.last_name}"
