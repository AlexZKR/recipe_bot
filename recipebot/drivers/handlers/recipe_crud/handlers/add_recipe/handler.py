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
from recipebot.drivers.handlers.recipe_crud.handlers.add_recipe.constants import (
    ADD_START,
    ADD_TITLE,
    CATEGORY,
    INGREDIENTS,
    STEPS,
    TAGS,
    TITLE,
)
from recipebot.drivers.handlers.recipe_crud.handlers.add_recipe.field_handlers import (
    add_tag_to_recipe,
    finalize_recipe,
    handle_cancel,
    handle_category,
    handle_ingredients,
    handle_steps,
    handle_tags,
    handle_title,
    show_tags_keyboard,
)
from recipebot.drivers.handlers.recipe_crud.handlers.from_tiktok.field_handlers import (
    finalize_tiktok_recipe,
)
from recipebot.drivers.handlers.recipe_crud.handlers.from_tiktok.handler_context import (
    TikTokRecipeContextKey,
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
    await context.bot.send_message(chat_id=query.message.chat.id, text=ADD_TITLE)

    return TITLE


# Global callback handler for tag operations during recipe creation
async def global_handle_tag_callbacks(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Global handler for tag-related callback queries during recipe creation."""
    query = update.callback_query
    if not query or not query.data:
        return

    # Only handle tag-related callbacks
    callback_data = query.data
    if not (
        callback_data.startswith("tag_") or callback_data in ["new_tag", "tags_done"]
    ):
        return  # Not a handled callback, let other handlers process it

    # Only handle if we're in recipe creation context (regular or TikTok)
    if not context.user_data or (
        "title" not in context.user_data
        and TikTokRecipeContextKey.PARSED_RECIPE not in context.user_data
    ):
        return

    await query.answer()

    if callback_data == "new_tag":
        await query.edit_message_text("Enter the name for your new tag:")
    elif callback_data == "tags_done":
        # Determine which finalization function to call based on context
        if TikTokRecipeContextKey.PARSED_RECIPE in context.user_data:
            # TikTok recipe creation
            await finalize_tiktok_recipe(update, context)
        else:
            # Regular recipe creation
            await finalize_recipe(update, context)
    elif callback_data.startswith("tag_"):
        tag_name = callback_data[4:]  # Remove "tag_" prefix
        print(f"DEBUG: Global handler - Adding tag '{tag_name}'")  # Debug
        try:
            await add_tag_to_recipe(context, tag_name)
            await show_tags_keyboard(update, context)
        except Exception as e:
            await query.edit_message_text(f"Error adding tag: {e}")


global_tag_callback_handler = CallbackQueryHandler(
    global_handle_tag_callbacks  # No pattern - catch all callbacks
)


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
        ],
    },
    fallbacks=[CommandHandler("cancel", handle_cancel)],
    persistent=True,
    name="add_recipe_conversation",
)
