from functools import wraps

import structlog
from telegram import ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes

from recipebot.drivers.state import get_state
from recipebot.ports.repositories.exceptions import UserNotFound

logger: structlog.BoundLogger = structlog.get_logger(__name__)
MSG_NOT_REGISTERED = "User must be registered in the bot to perform this action."


def only_registered(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            user_repo = get_state()["user_repo"]
            user = await user_repo.get_by_tg_user(update.effective_user)
            if not user:
                raise UserNotFound
            return await func(update, context)
        except UserNotFound as exc:
            if update.effective_chat:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=MSG_NOT_REGISTERED,
                    reply_markup=ReplyKeyboardRemove(),
                )
            logger.error(MSG_NOT_REGISTERED, exc_info=exc)
        except Exception as exc:
            logger.error("Authentication error", exc_info=exc)
            raise RuntimeError("System error")

    return wrapper
