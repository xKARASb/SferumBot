"""Unified bot for Sferum and Max message forwarding to Telegram."""

import asyncio
import sys
from os import getenv
from typing import Dict, Any

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import ClientSession
from dotenv import load_dotenv
from loguru import logger

# Import both implementations
try:
    from pymax import MaxClient, Message as PyMaxMessage
    PYMAX_AVAILABLE = True
    logger.info("PyMax is available")
except ImportError as e:
    logger.warning(f"PyMax import error: {e}")
    PYMAX_AVAILABLE = False
    MaxClient = None
    PyMaxMessage = None

from max.max_types import EventMessage, Message as MaxMessage
from tg.methods.send_message import send_message
from tg.methods.send_error import send_error
from max.methods import get_credentials, get_message
from max.test_messages import send_max_test_message
from max.sferum_test_messages import send_sferum_test_message
from max.test_message_types import TestMessage

# Load configuration
load_dotenv()

# Telegram configuration
BOT_TOKEN = getenv("BOT_TOKEN")
TG_CHAT_ID = getenv("TG_CHAT_ID")
TG_TOPIC_ID = int(getenv("TG_TOPIC_ID")) if getenv("TG_TOPIC_ID") else None

# Sferum configuration
SFERUM_AUTH_COOKIE = getenv("SFERUM_AUTH_COOKIE")
SFERUM_CHAT_ID = getenv("SFERUM_CHAT_ID")

# Max configuration
MAX_PHONE = getenv("MAX_PHONE")
MAX_CHAT_ID = getenv("MAX_CHAT_ID")

# Topic mapping
SFERUM_TOPIC_ID = int(getenv("SFERUM_TOPIC_ID", "1")) if getenv("SFERUM_TOPIC_ID", "1") else None  # Default to topic 1
MAX_TOPIC_ID = int(getenv("MAX_TOPIC_ID", "2")) if getenv("MAX_TOPIC_ID", "2") else None      # Default to topic 2


class UnifiedMessageForwarder:
    """Unified message forwarder for both Sferum and Max."""
    
    def __init__(self):
        self.sferum_client = None
        self.max_client = None
        
    async def initialize_clients(self):
        """Initialize both Sferum and Max clients."""
        # Initialize Sferum client (existing implementation)
        if SFERUM_AUTH_COOKIE and SFERUM_CHAT_ID:
            from sferum_client import get_credentials as sferum_get_credentials
            from sferum_client import get_message as sferum_get_message
            from max.methods.get_user import get_user_credentials as sferum_get_user
            
            sferum_session = ClientSession()
            sferum_user = await sferum_get_user(SFERUM_AUTH_COOKIE, sferum_session)
            sferum_access_token = sferum_user.access_token
            sferum_creds = await sferum_get_credentials(sferum_access_token, sferum_session)
            
            # Create a simple wrapper for Sferum
            self.sferum_creds = sferum_creds
            self.sferum_access_token = sferum_access_token
            self.sferum_session = sferum_session
                
        # Initialize Max client (PyMax)
        if PYMAX_AVAILABLE and MAX_PHONE:
            self.max_client = MaxClient(phone=MAX_PHONE, work_dir="cache")
            
        logger.info(f"Initialized Sferum: {'Yes' if self.sferum_creds else 'No'}")
        logger.info(f"Initialized Max: {'Yes' if self.max_client else 'No'}")
    
    async def start_sferum_listening(self, bot: Bot):
        """Start listening for Sferum messages."""
        if not self.sferum_creds:
            return
            
        from sferum_client import main as sferum_main
        
        await sferum_main(
            self.sferum_session,
            self.sferum_creds.server,
            self.sferum_creds.key,
            self.sferum_creds.ts,
            TG_CHAT_ID,
            SFERUM_CHAT_ID,
            self.sferum_access_token,
            SFERUM_AUTH_COOKIE,
            self.sferum_creds.pts,
            bot,
            TG_TOPIC_ID if TG_TOPIC_ID else SFERUM_TOPIC_ID,
        )
    
    async def start_max_listening(self, bot: Bot):
        """Start listening for Max messages using PyMax."""
        if not self.max_client:
            return
            
        allowed_chat_ids = {
            chat_id for chat_id in "".join(MAX_CHAT_ID.split()).split(",") if chat_id
        }
        
        logger.info(f"Starting Max client for chats: {allowed_chat_ids}")
        
        # Set up message handler
        async def max_message_handler(msg: PyMaxMessage):
            """Handle incoming messages from Max."""
            logger.info(f"Received message from Max: {msg}")
            
            # Check if message is from allowed chat
            msg_chat_id = getattr(msg, 'chat_id', 0)
            if str(msg_chat_id) not in allowed_chat_ids:
                logger.debug(f"Message from chat {msg_chat_id} not in allowed list")
                return
            
            # Convert PyMax message to our format
            max_msg = MaxMessage(
                text=getattr(msg, 'text', ''),
                user_id=getattr(msg, 'user_id', 0),
                chat_id=getattr(msg, 'chat_id', 0),
                msg_id=getattr(msg, 'id', 0),
                from_user=str(getattr(msg, 'from_user', '')),
                timestamp=getattr(msg, 'timestamp', 0),
                chat_title=getattr(msg, 'chat_title', f"Chat {msg_chat_id}")
            )
            
            # Send to Telegram with Max topic
            await send_message(bot, max_msg, TG_CHAT_ID, MAX_TOPIC_ID)
        
        # Add message handler
        self.max_client.add_message_handler(max_message_handler, filter=None)
        
        # Start Max client
        try:
            await self.max_client.connect()
            await self.max_client.start()
        except Exception as e:
            logger.error(f"Max client error: {e}")
            raise
    
    async def send_startup_test_messages(self, bot: Bot):
        """Send test messages on startup to verify connections."""
        status_message = "Unified Bot started. Status:\n"
        if self.sferum_creds:
            status_message += "✅ Sferum client initialized.\n"
        else:
            status_message += "❌ Sferum client not configured or failed to initialize.\n"
        
        if self.max_client:
            status_message += "✅ Max client initialized.\n"
        else:
            status_message += "❌ Max client not configured or failed to initialize.\n"
            
        # Create a TestMessage object for the status message

        
        # Send Sferum test message
        if self.sferum_creds and SFERUM_CHAT_ID:
            try:
                await send_sferum_test_message(
                    bot,
                    self.sferum_session,
                    SFERUM_CHAT_ID,
                    SFERUM_TOPIC_ID,
                    self.sferum_access_token
                )
                logger.info("Sferum test message sent successfully")
            except Exception as e:
                logger.error(f"Failed to send Sferum test message: {e}")
        
        # Send Max test message
        if self.max_client and MAX_CHAT_ID:
            try:
                # Get first chat ID from MAX_CHAT_ID (can be comma-separated)
                first_chat_id = MAX_CHAT_ID.split(',')[0].strip()
                await send_max_test_message(
                    bot,
                    self.max_client,
                    first_chat_id,
                    MAX_TOPIC_ID
                )
                logger.info("Max test message sent successfully")
            except Exception as e:
                logger.error(f"Failed to send Max test message: {e}")
    
    async def stop_listening(self):
        """Stop all clients."""
        if hasattr(self, 'sferum_session') and self.sferum_session:
            # Sferum cleanup would go here
            pass
            
        if self.max_client and hasattr(self.max_client, 'stop'):
            await self.max_client.stop()


async def main() -> None:
    """Unified bot startup function."""
    # Check required configuration
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is required")
        sys.exit()
        
    if not TG_CHAT_ID:
        logger.error("TG_CHAT_ID is required")
        sys.exit()
    
    if not (SFERUM_AUTH_COOKIE and SFERUM_CHAT_ID) and not (MAX_PHONE and MAX_CHAT_ID):
        logger.error("Either Sferum or Max configuration is required")
        sys.exit()
    
    # Connect logs file
    logger.level("DEBUG") # Set default logging level to DEBUG
    logger.add("unified_bot.log")
    
    try:
        # Creating bot
        bot = Bot(
            BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2),
        )
        
        # Initialize forwarder
        forwarder = UnifiedMessageForwarder()
        await forwarder.initialize_clients()
        
        logger.info("Unified Bot started")
        
        # Send startup test messages
        await forwarder.send_startup_test_messages(bot)
        
        # Start both clients concurrently
        tasks = []
        
        if forwarder.sferum_creds:
            tasks.append(asyncio.create_task(
                forwarder.start_sferum_listening(bot)
            ))
            
        if forwarder.max_client:
            tasks.append(asyncio.create_task(
                forwarder.start_max_listening(bot)
            ))
        
        if not tasks:
            logger.error("No clients configured")
            sys.exit()
        
        # Wait for tasks
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("Shutting down gracefully...")
        finally:
            await forwarder.stop_listening()
            await bot.close()
            
    except Exception as e:
        logger.exception(f"Fatal error in main: {e}")
        await send_error(bot, TG_CHAT_ID, TG_TOPIC_ID or SFERUM_TOPIC_ID or "1")


if __name__ == "__main__":
    asyncio.run(main())