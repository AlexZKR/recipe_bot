from telegram import Update
from telegram.ext import ContextTypes

from recipebot.drivers.handlers.main_keyboard import MAIN_KEYBOARD


async def show_category_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show category selection (placeholder - not implemented yet)."""
    if not update.effective_chat:
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Category search is not implemented yet. Please use tag search.",
        reply_markup=MAIN_KEYBOARD,
    )
