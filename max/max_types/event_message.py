"""Event message object for Max Messenger."""


class EventMessage:
    """Event message class for Max Messenger."""
    
    def __init__(self, type, msg_id, flags, peer, value, title, text, *args, **kwargs) -> None:
        """Initialize event message."""
        self.type = type
        self.msg_id = msg_id
        self.flags = flags
        self.chat_id = peer
        self.text = text
        self.title = title
        self.__dict__.update(kwargs)
    
    def __repr__(self) -> str:
        """String representation of event message."""
        return f"from {self.title}: {self.text}, chat id: {self.chat_id}"