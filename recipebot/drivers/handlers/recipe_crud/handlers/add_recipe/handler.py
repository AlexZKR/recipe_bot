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
from recipebot.drivers.handlers.basic_fallback import (
    basic_fallback_handler,
    get_cancel_handler,
)
from recipebot.drivers.handlers.recipe_crud.handlers.add_recipe.constants import (
    ADD_CANCEL,
    ADD_START,
    ADD_TITLE,
    CATEGORY,
    INGREDIENTS,
    STEPS,
    TAGS,
    TITLE,
)
from recipebot.drivers.handlers.recipe_crud.handlers.add_recipe.field_handlers import (
    handle_category,
    handle_ingredients,
    handle_steps,
    handle_tags,
    handle_title,
)
from recipebot.drivers.handlers.recipe_crud.handlers.from_tiktok.handler_context import (
    TikTokRecipeContextKey,
)
from recipebot.drivers.handlers.recipe_crud.shared_tag_callbacks import (
    global_tag_callback_handler,
)


async def _handle_start_manual_entry_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Entry point for add_recipe conversation from manual entry callback."""
    query = update.callback_query
    if not query:
        return ConversationHandler.END

    await query.answer()

    # Check if this is coming from failed TikTok parsing
    if context.user_data and context.user_data.get(
        TikTokRecipeContextKey.PENDING_TIKTOK_DATA
    ):
        # Transfer the pending TikTok data to the current context
        pending_data = context.user_data.pop(TikTokRecipeContextKey.PENDING_TIKTOK_DATA)
        context.user_data.update(pending_data)

    # Send the start message
    await query.edit_message_text(ADD_START)
    if query.message:
        await context.bot.send_message(chat_id=query.message.chat.id, text=ADD_TITLE)

    return TITLE


@only_registered
async def add_recipe_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks for a title."""
    if not update.effective_chat:
        raise Exception("No chat in the update")

    # Check if this is coming from failed TikTok parsing
    if context.user_data and context.user_data.get(
        TikTokRecipeContextKey.PENDING_TIKTOK_DATA
    ):
        # Transfer the pending TikTok data to the current context
        pending_data = context.user_data.pop(TikTokRecipeContextKey.PENDING_TIKTOK_DATA)
        context.user_data.update(pending_data)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=ADD_START)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=ADD_TITLE)

    return TITLE


# Conversation handler for adding recipes
add_recipe_handler = ConversationHandler(
    entry_points=[
        CommandHandler("add", add_recipe_start),
        CallbackQueryHandler(
            _handle_start_manual_entry_callback, pattern="^start_manual_entry$"
        ),
    ],
    states={
        TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_title)],
        INGREDIENTS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ingredients)
        ],
        STEPS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_steps)],
        CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_category)],
        TAGS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tags),
            global_tag_callback_handler,
        ],
    },
    fallbacks=[
        CommandHandler("cancel", get_cancel_handler(ADD_CANCEL)),
        basic_fallback_handler,  # type: ignore[list-item]
    ],
    persistent=True,
    name="add_recipe_conversation",
)
