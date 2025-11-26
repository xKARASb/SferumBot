"""Send error to telegram."""

from loguru import logger
from aiogram import Bot


async def send_error(
    bot: Bot,
    tg_chat_id: str,
    tg_topic_id: int | None = None,
) -> None:
    """Send error message to telegram."""
    try:
        error_msg = "⚠️ Произошла ошибка при обработке сообщений из Макс"
        await bot.send_message(
            tg_chat_id,
            error_msg,
            message_thread_id=tg_topic_id
        )
        logger.error("Error message sent to Telegram")
    except Exception as e:
        logger.exception(f"Failed to send error message: {e}")