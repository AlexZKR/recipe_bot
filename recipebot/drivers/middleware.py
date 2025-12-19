"""Middleware handlers for request processing."""

from telegram import Update
from telegram.ext import ContextTypes, TypeHandler

from recipebot.config.logging.filters import (
    clear_telegram_context,
    set_telegram_context,
)


# Middleware handler for logging context (runs first for all updates)
async def logging_middleware(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Middleware that automatically sets up logging context for ALL requests.

    This runs before any other handler and populates thread-local logging context
    with user information, making it available to all subsequent log calls.
    """
    # Clear any existing context and set fresh context for this request
    clear_telegram_context()
    set_telegram_context(update, context)
    # Note: This handler doesn't return True, so processing continues to other handlers


# Create middleware handler that matches ALL updates
logging_middleware_handler = TypeHandler(Update, logging_middleware)
