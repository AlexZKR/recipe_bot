"""Tag display utilities for tag search functionality."""

from telegram import InlineKeyboardButton, Update
from telegram.ext import ContextTypes

from recipebot.drivers.handlers.main_keyboard import MAIN_KEYBOARD
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.handler_context import (
    SearchRecipesCallbackPattern,
)
from recipebot.drivers.handlers.recipe_crud.shared import (
    PaginatedResult,
    create_paginated_keyboard,
)
from recipebot.drivers.state import get_state


async def show_tag_selection(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    page: int = 1,
    edit_message: bool = False,
):
    """Show paginated list of available tags for search."""
    if not update.effective_chat or not update.effective_user:
        raise Exception("Not chat or user in the update")

    recipe_repo = get_state()["recipe_repo"]
    tags = await recipe_repo.get_user_tags(update.effective_user.id)

    if not tags:
        message = "You don't have any tags yet. Add some tags to your recipes first!"
        if edit_message and update.callback_query:
            await update.callback_query.edit_message_text(message)
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
            )
        return

    # Create paginated result for tags
    paginated_result = PaginatedResult(
        tags,
        page,
        callback_prefix=SearchRecipesCallbackPattern.TAG_PREFIX,
        item_type="tags",
    )

    # Create paginated keyboard
    def item_callback_factory(tag, current_page):
        return f"{SearchRecipesCallbackPattern.TAG_PREFIX}{tag.name}"

    reply_markup = create_paginated_keyboard(
        paginated_result,
        item_callback_factory,
        navigation_prefix=SearchRecipesCallbackPattern.TAG_PAGE_PREFIX,
        additional_buttons=[
            InlineKeyboardButton(
                "⬅️ Back to mode selection",
                callback_data=f"{SearchRecipesCallbackPattern.MODE_PREFIX}",
            )
        ],
    )

    message_text = f"Select a tag to search for recipes:\n\n{paginated_result.get_page_info_text()}"

    if edit_message and update.callback_query:
        await update.callback_query.edit_message_text(
            message_text,
            reply_markup=reply_markup,
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message_text,
            reply_markup=reply_markup,
        )

        # Also show the main keyboard below
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Or use the keyboard below:",
            reply_markup=MAIN_KEYBOARD,
        )
