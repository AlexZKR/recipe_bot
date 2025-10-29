from functools import wraps
from logging import getLogger

from telegram import Update
from telegram.ext import ContextTypes

from recipebot.adapters.repositories.sql.auth.exceptions import UserNotFound
from recipebot.drivers.state import get_state

logger = getLogger(__name__)


def only_registered(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            user_repo = get_state(context)["user_repo"]
            await user_repo.get_by_tg_user(update.effective_user)
        except UserNotFound:
            if update.effective_chat:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="User must be registered in the bot to perform this action.",
                )
            logger.exception(
                "User must be registered in the bot to perform this action"
            )
        except Exception as exc:
            logger.error(exc)
            raise RuntimeError("System error")

        return await func(update, context)

    return wrapper
