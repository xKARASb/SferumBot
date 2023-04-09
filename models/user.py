from sqlalchemy import Column, Integer, String, ForeignKey

from models.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    cookie = Column(String)
    peer = Column(Integer)
    chat_id = Column(Integer)
    vk_id = Column(Integer)

    def __init__(self, id: int, cookie: str, peer: int, chat_id: int, vk_id: int) -> None:
        self.id = id
        self.vk_id = vk_id
        self.cookie = cookie
        self.peer = peer
        self.chat_id = chat_id

    def __repr__(self) -> str:
        info: str = f"id: {self.id}, cookie: {self.cookie}, peer: {self.peer}, chat_id: {self.chat_id}, vk_id: {self.vk_id}"
        return info