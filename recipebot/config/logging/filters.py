"""Logging filters for adding context to log records."""

import logging
import threading

from telegram import Update
from telegram.ext import ContextTypes

from recipebot.config.logging.json_logging import safe_serialize_value

# Thread-local storage for current request context
_local = threading.local()


class TelegramContextFilter(logging.Filter):
    """Filter that adds Telegram context to all log records."""

    def filter(self, record):
        record.user_id = getattr(_local, "user_id", None)
        record.chat_id = getattr(_local, "chat_id", None)
        record.username = getattr(_local, "username", None)
        record.user_data = getattr(_local, "user_data", None)
        return True


def set_telegram_context(
    update: Update, context: ContextTypes.DEFAULT_TYPE | None = None
) -> None:
    """Set Telegram context for automatic logging in all subsequent log calls.

    Usage:
        set_telegram_context(update, context)
        logger.info("This will automatically include user/chat context")
        logger.debug("This too!")
    """
    if update.effective_user:
        _local.user_id = update.effective_user.id
    if update.effective_chat:
        _local.chat_id = update.effective_chat.id
    if update.effective_user:
        _local.username = update.effective_user.username or "no_username"

    # Safely extract user_data if context is provided
    if context and hasattr(context, "user_data") and context.user_data:
        try:
            # Create a safe copy of user_data for logging
            _local.user_data = safe_serialize_value(dict(context.user_data))
        except Exception:
            # If serialization fails, don't include user_data
            _local.user_data = {"error": "could_not_serialize"}
    if context and hasattr(context, "user_data") and context.user_data:
        _local.user_data = context.user_data


def clear_telegram_context() -> None:
    """Clear the Telegram context."""
    if hasattr(_local, "user_id"):
        delattr(_local, "user_id")
    if hasattr(_local, "chat_id"):
        delattr(_local, "chat_id")
    if hasattr(_local, "username"):
        delattr(_local, "username")
    if hasattr(_local, "user_data"):
        delattr(_local, "user_data")
