from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters


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


basic_fallback_handler = MessageHandler(filters.TEXT, handle_unknown_command)
