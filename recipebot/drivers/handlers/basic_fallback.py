from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters

from recipebot.drivers.handlers.main_keyboard import MAIN_KEYBOARD


async def handle_unknown_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle unknown user input to prevent being stuck in a conversation."""
    if not update.effective_chat:
        raise Exception("No chat in the update")

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry, I didn't understand that command. Please try again. If you feel being stuck, use /cancel cmd to start over.",
    )


async def handle_cancel(
    update: Update, context: ContextTypes.DEFAULT_TYPE, cancel_msg: str
) -> int:
    """Cancels and ends the conversation."""
    if context.user_data is None:
        raise Exception("Something went wrong")
    if not update.message:
        raise Exception("No message in the update")

    await update.message.reply_text(cancel_msg, reply_markup=MAIN_KEYBOARD)
    context.user_data.clear()
    return ConversationHandler.END


basic_fallback_handler = MessageHandler(filters.TEXT, handle_unknown_command)


def get_cancel_handler(cancel_msg: str):
    async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        return await handle_cancel(update, context, cancel_msg)

    return cancel_handler
