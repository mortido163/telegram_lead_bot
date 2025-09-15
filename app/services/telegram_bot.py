import logging

from aiogram import Bot

logger = logging.getLogger(__name__)


def create_bot(token: str | None) -> Bot | None:
    if not token:
        logger.warning("BOT_TOKEN is not set; Telegram bot will be disabled")
        return None
    try:
        return Bot(token=token)
    except Exception as e:
        # Invalid token or aiogram not ready; skip bot initialization
        logger.warning("Invalid BOT_TOKEN; Telegram bot disabled: %s", e)
        return None
