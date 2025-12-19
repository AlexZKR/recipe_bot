"""Generic filter selection display utilities."""

from collections.abc import Awaitable, Callable
from typing import Any

from telegram import InlineKeyboardButton, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from recipebot.drivers.handlers.main_keyboard import MAIN_KEYBOARD
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.handler_context import (
    SearchRecipesFilterOperation,
)
from recipebot.drivers.handlers.recipe_crud.shared import (
    PaginatedResult,
    create_paginated_keyboard,
)


async def show_generic_filter_selection(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    item_getter: Callable[[int], Awaitable[list[Any]]],
    selected_user_data_key: str,
    callback_prefix: str,
    page_prefix: str,
    item_type: str,
    back_callback_data: str,
    page: int = 1,
    edit_message: bool = True,
    show_main_keyboard: bool = True,
    message_template: str | None = None,
):
    """Generic function to show paginated filter selection with add/remove buttons.

    Args:
        update: Telegram update
        context: Telegram context
        item_getter: Function that takes user_id and returns list of available items
        selected_user_data_key: Key in user_data for storing selected items
        callback_prefix: Prefix for item callback data
        page_prefix: Prefix for pagination callback data
        item_type: Type name for display ("tags", "categories", etc.)
        back_callback_data: Callback data for back button
        page: Current page number
        edit_message: Whether to edit existing message
        show_main_keyboard: Whether to show main keyboard below
    """
    if not update.effective_chat or not update.effective_user:
        raise Exception("Not chat or user in the update")

    # Get available items
    items = await item_getter(update.effective_user.id)

    if not items:
        message = f"You don't have any {item_type} yet. Add some {item_type} to your recipes first!"
        if edit_message and update.callback_query:
            await update.callback_query.edit_message_text(message)
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
            )
        return

    # Get currently selected items
    selected_items: list[str] = (
        context.user_data.get(selected_user_data_key, []) if context.user_data else []
    )

    # Create paginated result
    paginated_result = PaginatedResult(
        items,
        page,
        item_type=item_type,
    )

    def item_callback_factory(item, current_page):
        """Check if item is already selected and return appropriate callback data."""
        # Handle different item types (RecipeTag has name, RecipeCategory has value, etc.)
        item_name = getattr(item, "name", getattr(item, "value", str(item)))
        is_selected = item_name in selected_items
        operation = (
            SearchRecipesFilterOperation.REMOVE
            if is_selected
            else SearchRecipesFilterOperation.ADD
        )
        return f"{callback_prefix}{operation}__{item_name}__{current_page}"

    def display_text_factory(item, current_page):
        """Check if item is already selected and show appropriate emoji."""
        # Handle different item types
        item_name = getattr(item, "name", getattr(item, "value", str(item)))
        is_selected = item_name in selected_items
        emoji = "❌" if is_selected else "➕"
        return f"{emoji} {item_name}"

    reply_markup = create_paginated_keyboard(
        paginated_result,
        item_callback_factory,
        navigation_prefix=page_prefix,
        additional_buttons=[
            InlineKeyboardButton(
                "🔙 Back to mode selection",
                callback_data=back_callback_data,
            )
        ],
        display_text_factory=display_text_factory,
    )

    # Create message - use template if provided, otherwise generic
    if message_template:
        message = message_template
    else:
        current_filters = []
        if selected_items:
            current_filters.append(f"Selected {item_type}: {', '.join(selected_items)}")

        filters_text = (
            "\n\n".join(current_filters)
            if current_filters
            else f"No {item_type} selected yet."
        )
        message = f"Select {item_type} to filter recipes:\n\n{filters_text}"

    if edit_message and update.callback_query:
        await update.callback_query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML,
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML,
        )

        if show_main_keyboard:
            # Also show the main keyboard below
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Or use the keyboard below:",
                reply_markup=MAIN_KEYBOARD,
                parse_mode=ParseMode.HTML,
            )
