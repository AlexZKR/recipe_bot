"""Tag display utilities for tag search functionality."""

from telegram import InlineKeyboardButton, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from recipebot.drivers.handlers.main_keyboard import MAIN_KEYBOARD
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.handler_context import (
    SearchRecipesCallbackPattern,
    SearchRecipesContextKey,
    SearchRecipesFilterOperation,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.messages import (
    TAG_SELECTION_MESSAGE,
    get_current_filters_message,
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
    edit_message: bool = True,
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

    # Get currently selected tags
    selected_tags: list[str] = (
        context.user_data.get(SearchRecipesContextKey.SELECTED_TAGS, [])
        if context.user_data
        else []
    )

    # Create paginated result for tags
    paginated_result = PaginatedResult(
        tags,
        page,
        item_type="tags",
    )

    def item_callback_factory(tag, current_page):
        """Check if tag is already selected and return appropriate callback data."""
        is_selected = tag.name in selected_tags
        operation = (
            SearchRecipesFilterOperation.REMOVE
            if is_selected
            else SearchRecipesFilterOperation.ADD
        )
        return f"{SearchRecipesCallbackPattern.TAG_PREFIX}{operation}__{tag.name}__{current_page}"

    def display_text_factory(tag, current_page):
        """Check if tag is already selected and show appropriate emoji."""
        is_selected = tag.name in selected_tags
        emoji = "❌" if is_selected else "➕"
        return f"{emoji} {tag.name}"

    reply_markup = create_paginated_keyboard(
        paginated_result,
        item_callback_factory,
        navigation_prefix=SearchRecipesCallbackPattern.TAG_PAGE_PREFIX,
        additional_buttons=[
            InlineKeyboardButton(
                "🔙 Back to mode selection",
                callback_data=f"{SearchRecipesCallbackPattern.MODE_PREFIX}",
            )
        ],
        display_text_factory=display_text_factory,
    )

    if edit_message and update.callback_query:
        await update.callback_query.edit_message_text(
            TAG_SELECTION_MESSAGE.format(
                current_filters=get_current_filters_message(context)
            ),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML,
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=TAG_SELECTION_MESSAGE.format(
                current_filters=get_current_filters_message(context)
            ),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML,
        )

        # Also show the main keyboard below
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Or use the keyboard below:",
            reply_markup=MAIN_KEYBOARD,
            parse_mode=ParseMode.HTML,
        )
