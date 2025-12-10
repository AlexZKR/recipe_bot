from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from recipebot.drivers.handlers.auth.decorators import only_registered
from recipebot.drivers.handlers.basic_fallback import basic_fallback_handler
from recipebot.drivers.handlers.recipe_crud.handlers.from_tiktok.constants import (
    CATEGORY,
    MANUAL_ENTRY,
    PROCESSING,
    SAVE,
    TAGS,
    TIKTOK_START,
    URL,
)
from recipebot.drivers.handlers.recipe_crud.handlers.from_tiktok.field_handlers import (
    handle_cancel,
    handle_category,
    handle_manual_entry_callback,
    handle_tags,
    handle_tiktok_url,
)
from recipebot.drivers.handlers.recipe_crud.shared_tag_callbacks import (
    global_tag_callback_handler,
)


@only_registered
async def from_tiktok_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks for a TikTok URL."""
    if not update.effective_chat:
        raise Exception("No chat in the update")

    await context.bot.send_message(chat_id=update.effective_chat.id, text=TIKTOK_START)

    return URL


# Conversation handler for creating recipes from TikTok
from_tiktok_handler = ConversationHandler(
    entry_points=[CommandHandler("from_tiktok", from_tiktok_start)],
    states={
        URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tiktok_url)],
        PROCESSING: [],  # This state is handled internally
        MANUAL_ENTRY: [
            CallbackQueryHandler(
                handle_manual_entry_callback, pattern="^(manual_entry|cancel_manual)$"
            )
        ],
        CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_category)],
        TAGS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tags),
            global_tag_callback_handler,
        ],
        SAVE: [],  # This state is handled internally
    },
    fallbacks=[CommandHandler("cancel", handle_cancel), basic_fallback_handler],
    persistent=True,
    name="from_tiktok_conversation",
)

# Export the handlers
__all__ = ["from_tiktok_handler"]
