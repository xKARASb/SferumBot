"""Test message types for startup verification."""

from dataclasses import dataclass


@dataclass
class TestMessage:
    """Simple test message for startup verification."""
    text: str
    user_id: int
    chat_id: str
    msg_id: int
    from_user: str
    timestamp: int
    chat_title: str