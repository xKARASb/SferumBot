"""Test message utilities for Sferum startup verification."""

import asyncio
import os
from typing import Optional
from aiohttp import ClientSession
from loguru import logger

from max.max_types import Message as MaxMessage
from tg.methods.send_message import send_message


async def send_sferum_test_message(bot, session: ClientSession, chat_id: str, topic_id: str, access_token: str) -> bool:
    """
    Send a test message from Sferum to verify connection.
    
    Args:
        bot: Telegram bot instance
        session: Sferum HTTP session
        chat_id: Sferum chat ID
        topic_id: Telegram topic ID
        access_token: Sferum access token
        
    Returns:
        bool: Success status
    """
    try:
        # Create a diagnostic test message
        from max.test_message_types import TestMessage
        test_msg = TestMessage(
            text=f"✅ Max2TG бот успешно запущен!\n\n📱 Чат Сферум: {chat_id}\n🔄 Пересылка сообщений активна\n⏰ Время запуска: {asyncio.get_event_loop().time()}",
            user_id=0,
            chat_id=chat_id,
            msg_id=0,
            from_user="Max2TG System",
            timestamp=0,
            chat_title=f"Sferum Chat {chat_id}"
        )
        
        # Send diagnostic message to Telegram
        await send_message(bot, test_msg, os.getenv("TG_CHAT_ID"), topic_id)
        logger.info(f"Diagnostic test message sent for Sferum chat {chat_id}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error sending Sferum test message: {e}")
        return False

