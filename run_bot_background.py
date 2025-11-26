#!/usr/bin/env python3
"""
Background runner for Max2TG bot with logging support.
"""

import asyncio
import sys
import os
from signal import SIGINT, SIGTERM
import signal
from loguru import logger

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unified_bot import main as bot_main


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)


async def main():
    """Main function for background execution."""
    # Configure logging
    logger.add(
        "max2tg.log",
        rotation="10 MB",
        retention="10 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        encoding="utf-8"
    )
    
    logger.info("🚀 Starting Max2TG bot in background mode")
    logger.info("📝 Logs will be written to max2tg.log")
    logger.info("🔍 Monitor this file for message forwarding status")
    
    # Set up signal handlers
    signal.signal(SIGINT, signal_handler)
    signal.signal(SIGTERM, signal_handler)
    
    try:
        # Run the main bot
        await bot_main()
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user (KeyboardInterrupt)")
    except Exception as e:
        logger.error(f"💥 Bot crashed with error: {e}")
        raise
    finally:
        logger.info("🏁 Bot shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Background runner stopped")
        sys.exit(0)
    except Exception as e:
        logger.error(f"💥 Fatal error in background runner: {e}")
        sys.exit(1)