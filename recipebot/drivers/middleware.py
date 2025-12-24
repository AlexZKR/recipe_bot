import structlog
from structlog.contextvars import bind_contextvars
from telegram import Update
from telegram.ext import ContextTypes, TypeHandler


def bind_telegram_context(
    update: Update, context: ContextTypes.DEFAULT_TYPE | None = None
) -> None:
    if update.effective_user:
        bind_contextvars(user_id=update.effective_user.id)
    if update.effective_chat:
        bind_contextvars(chat_id=update.effective_chat.id)
    if update.effective_user:
        bind_contextvars(username=update.effective_user.username or "no_username")
    if context and context.user_data:
        bind_contextvars(user_data=context.user_data)


async def logging_middleware(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    structlog.contextvars.clear_contextvars()
    bind_telegram_context(update, context)


logging_middleware_handler = TypeHandler(Update, logging_middleware)
