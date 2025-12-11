from logging import getLogger

from telegram import ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes

from recipebot.config import settings
from recipebot.drivers.handlers.auth.decorators import only_registered
from recipebot.drivers.handlers.auth.messages import REGISTER_SUCCESS
from recipebot.drivers.handlers.main_keyboard import MAIN_KEYBOARD
from recipebot.drivers.state import get_state
from recipebot.ports.repositories.exceptions import RepositoryException

logger = getLogger(__name__)


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat:
        raise Exception("Not chat in the update")
    user_repo = get_state()["user_repo"]
    if not update.effective_user:
        raise Exception("No user in the update")
    try:
        logger.info(f"Tester IDs: {settings.APP.tester_ids}")
        if update.effective_user.id not in settings.APP.tester_ids:
            logger.warning(f"User {update.effective_user.id} is not a tester")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="You are not a tester. Contact the administrator to get access.",
                reply_markup=ReplyKeyboardRemove(),
            )
            return
        await user_repo.add(register_data=update.effective_user)
    except RepositoryException as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=str(e),
            reply_markup=MAIN_KEYBOARD,
        )
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=REGISTER_SUCCESS,
        reply_markup=MAIN_KEYBOARD,
    )


@only_registered
async def for_registered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat:
        raise Exception("Not chat in the update")

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="You are registered in the bot!",
        reply_markup=MAIN_KEYBOARD,
    )
