"""Test message utilities for Max2TG startup verification."""

import asyncio
import os
from typing import Optional
from loguru import logger
from pymax import MaxClient

from max.max_types import Message as MaxMessage
from tg.methods.send_message import send_message





async def send_max_test_message(bot, client: MaxClient, chat_id: str, topic_id: str) -> bool:
    """
    Send a test message from Max to verify connection.
    
    Args:
        bot: Telegram bot instance
        client: PyMax client
        chat_id: Max chat ID
        topic_id: Telegram topic ID
        
    Returns:
        bool: Success status
    """
    try:
        # Create a diagnostic test message
        from max.test_message_types import TestMessage
        test_msg = TestMessage(
            text=f"✅ Max2TG бот успешно запущен!\n\n📱 Чат Max: {chat_id}\n🔄 Пересылка сообщений активна\n⏰ Время запуска: {asyncio.get_event_loop().time()}",
            user_id=0,
            chat_id=chat_id,
            msg_id=0,
            from_user="Max2TG System",
            timestamp=0,
            chat_title=f"Max Chat {chat_id}"
        )
        
        # Send diagnostic message to Telegram
        await send_message(bot, test_msg, os.getenv("TG_CHAT_ID"), topic_id)
        logger.info(f"Diagnostic test message sent for Max chat {chat_id}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error sending Max test message: {e}")
        return False