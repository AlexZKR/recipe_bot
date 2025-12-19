"""Generic filter selection display utilities."""

from telegram import InlineKeyboardButton, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from recipebot.drivers.handlers.main_keyboard import MAIN_KEYBOARD
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.filter_selection_utils.filter_profile import (
    FilterProfile,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.handler_context import (
    SearchRecipesFilterOperation,
)
from recipebot.drivers.handlers.recipe_crud.shared import (
    PaginatedResult,
    create_paginated_keyboard,
)


async def _get_available_items(update: Update, profile: FilterProfile):
    """Get available items and handle empty case."""
    if not update.effective_user:
        raise Exception("No effective user in update")
    items = await profile.item_getter(update.effective_user.id)

    if not items:
        message = f"You don't have any {profile.item_type} yet. Add some {profile.item_type} to your recipes first!"
        return None, message

    return items, None


def _get_selected_items(
    context: ContextTypes.DEFAULT_TYPE, profile: FilterProfile
) -> list[str]:
    """Get currently selected items from context."""
    return (
        context.user_data.get(profile.selected_user_data_key, [])
        if context.user_data
        else []
    )


def _create_item_callback_factory(selected_items: list[str], profile: FilterProfile):
    """Create the callback factory function for filter items."""

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
        return f"{profile.callback_prefix}{operation}__{item_name}__{current_page}"

    return item_callback_factory


def _create_display_text_factory(selected_items: list[str], profile: FilterProfile):
    """Create the display text factory function for filter items."""

    def display_text_factory(item, current_page):
        """Check if item is already selected and show appropriate emoji."""
        # Handle different item types
        item_name = getattr(item, "name", getattr(item, "value", str(item)))
        is_selected = item_name in selected_items
        emoji = "❌" if is_selected else "➕"
        return f"{emoji} {item_name}"

    return display_text_factory


def _create_filter_keyboard(
    paginated_result,
    item_callback_factory,
    display_text_factory,
    profile: FilterProfile,
):
    """Create the paginated keyboard for filter selection."""
    return create_paginated_keyboard(
        paginated_result,
        item_callback_factory,
        navigation_prefix=profile.page_prefix,
        additional_buttons=[
            InlineKeyboardButton(
                "🔙 Back to mode selection",
                callback_data=profile.back_callback_data,
            )
        ],
        display_text_factory=display_text_factory,
    )


def _create_filter_message(
    selected_items: list[str],
    profile: FilterProfile,
    message_template: str | None = None,
):
    """Create the message for filter selection."""
    if message_template:
        return message_template

    current_filters = []
    if selected_items:
        current_filters.append(
            f"Selected {profile.item_type}: {', '.join(selected_items)}"
        )

    filters_text = (
        "\n\n".join(current_filters)
        if current_filters
        else f"No {profile.item_type} selected yet."
    )
    return f"Select {profile.item_type} to filter recipes:\n\n{filters_text}"


async def _send_filter_message(  # noqa: PLR0913
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    message: str,
    reply_markup,
    edit_message: bool,
    profile: FilterProfile,
):
    """Send or edit the filter selection message."""
    if not update.effective_chat:
        raise Exception("No effective chat in update")

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

        if profile.show_main_keyboard:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Or use the keyboard below:",
                reply_markup=MAIN_KEYBOARD,
                parse_mode=ParseMode.HTML,
            )


async def show_generic_filter_selection(  # noqa: PLR0913
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    profile: FilterProfile,
    page: int = 1,
    edit_message: bool = True,
    message_template: str | None = None,
):
    """Generic function to show paginated filter selection with add/remove buttons.

    Args:
        update: Telegram update
        context: Telegram context
        profile: Filter profile containing all configuration for filtering mode
        page: Current page number
        edit_message: Whether to edit existing message
        message_template: Optional custom message template
    """
    if not update.effective_chat or not update.effective_user:
        raise Exception("Not chat or user in the update")

    # Get available items
    items, error_message = await _get_available_items(update, profile)
    if error_message:
        if edit_message and update.callback_query:
            await update.callback_query.edit_message_text(error_message)
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=error_message,
            )
        return

    # Get selected items
    selected_items = _get_selected_items(context, profile)

    # Create paginated result
    paginated_result = PaginatedResult(
        items,
        page,
        item_type=profile.item_type,
    )

    # Create factories
    item_callback_factory = _create_item_callback_factory(selected_items, profile)
    display_text_factory = _create_display_text_factory(selected_items, profile)

    # Create keyboard
    reply_markup = _create_filter_keyboard(
        paginated_result, item_callback_factory, display_text_factory, profile
    )

    # Create message
    message = _create_filter_message(selected_items, profile, message_template)

    # Send message
    await _send_filter_message(
        update, context, message, reply_markup, edit_message, profile
    )
