"""Shared tag callback handlers for recipe creation conversations."""

from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from recipebot.drivers.handlers.recipe_crud.handlers.add_recipe.field_handlers import (
    add_tag_to_recipe,
    finalize_recipe,
    show_tags_keyboard,
)
from recipebot.drivers.handlers.recipe_crud.handlers.from_tiktok.field_handlers import (
    finalize_tiktok_recipe,
)
from recipebot.drivers.handlers.recipe_crud.handlers.from_tiktok.handler_context import (
    TikTokRecipeContextKey,
)


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
        return  # Not a tag callback, let other handlers process it

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
            return await finalize_tiktok_recipe(update, context)
        else:
            # Regular recipe creation
            return await finalize_recipe(update, context)
    elif callback_data.startswith("tag_"):
        tag_name = callback_data[4:]  # Remove "tag_" prefix
        try:
            await add_tag_to_recipe(context, tag_name)
            await show_tags_keyboard(update, context)
        except Exception as e:
            await query.edit_message_text(f"Error adding tag: {e}")


# Create the handler instance
global_tag_callback_handler = CallbackQueryHandler(
    global_handle_tag_callbacks,
    pattern=r"^(tag_[^ ]+|new_tag|tags_done)$",
)
