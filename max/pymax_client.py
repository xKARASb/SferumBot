"""PyMax client integration for max2tg."""

from typing import Optional, List, Dict, Any
from asyncio import Queue, Event
from loguru import logger

from pymax import MaxClient, Message as PyMaxMessage
PYMAX_AVAILABLE = True


class MaxAPIWrapper:
    """Wrapper for PyMax client to integrate with existing max2tg architecture."""
    
    def __init__(self, phone: str):
        """Initialize PyMax client."""
        if not PYMAX_AVAILABLE:
            raise ImportError("PyMax is required. Install with: pip install PyMax")
        
        self.client = MaxClient(phone=phone, work_dir="cache")
        self.message_queue = Queue()
        self._running = False
        
    async def start_listening(self) -> None:
        """Start listening for messages."""
        if not PYMAX_AVAILABLE:
            raise RuntimeError("PyMax not available")
            
        self._running = True
        
        # Set up message handler
        async def message_handler(msg: PyMaxMessage):
            """Handle incoming messages from PyMax."""
            logger.info(f"Received message from PyMax: {msg}")
            await self.message_queue.put(msg)
            
        self.client.on_message(message_handler)
        
        # Start the client
        try:
            await self.client.start()
        except Exception as e:
            logger.error(f"PyMax client error: {e}")
            self._running = False
            raise
    
    async def stop_listening(self) -> None:
        """Stop listening for messages."""
        self._running = False
        if hasattr(self.client, 'stop'):
            await self.client.stop()
    
    async def get_messages(self) -> List[PyMaxMessage]:
        """Get messages from queue."""
        messages = []
        while not self.message_queue.empty():
            try:
                msg = self.message_queue.get_nowait()
                messages.append(msg)
            except Exception as e:
                logger.error(f"Error getting message from queue: {e}")
                break
        return messages
    
    async def send_message(self, chat_id: int, text: str) -> bool:
        """Send message (not needed for this project, but for completeness)."""
        if not PYMAX_AVAILABLE:
            return False
            
        try:
            await self.client.send_message(chat_id, text)
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def is_running(self) -> bool:
        """Check if client is running."""
        return self._running


# Compatibility functions to work with existing architecture
async def create_max_client(phone: str) -> MaxAPIWrapper:
    """Create Max client wrapper."""
    return MaxAPIWrapper(phone)


def convert_pymax_to_max_message(pymax_msg: PyMaxMessage) -> 'Message':
    """Convert PyMax message to our Message format."""
    from max.max_types import Message
    
    # Create a mock Message object that matches our expected format
    msg = Message()
    
    # Map PyMax fields to our Message format
    # This will need to be adapted based on actual PyMax Message structure
    msg.text = getattr(pymax_msg, 'text', '')
    msg.sender_id = getattr(pymax_msg, 'from_id', 0)
    msg.date = getattr(pymax_msg, 'date', 0)
    msg.attachments = getattr(pymax_msg, 'attachments', [])
    msg.chat_msg_id = getattr(pymax_msg, 'id', 0)
    
    # Set full name if available
    if hasattr(pymax_msg, 'from_name'):
        msg.full_name = pymax_msg.from_name
    else:
        msg.full_name = str(pymax_msg.sender_id)
    
    return msg