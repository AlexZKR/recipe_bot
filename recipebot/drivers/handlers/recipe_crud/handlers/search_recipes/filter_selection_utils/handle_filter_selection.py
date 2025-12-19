"""Generic filter selection callback handlers."""

import logging
from collections.abc import Awaitable, Callable

from telegram import Update
from telegram.ext import ContextTypes

from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.filter_selection_utils.constants import (
    FILTER_CALLBACK_PARTS,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.handler_context import (
    SearchRecipesFilterOperation,
)

logger = logging.getLogger(__name__)


async def handle_generic_filter_selection(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    callback_prefix: str,
    selected_user_data_key: str,
    show_function: Callable[[Update, ContextTypes.DEFAULT_TYPE, int], Awaitable[None]],
):
    """Generic handler for filter selection callbacks (add/remove items).

    Args:
        update: Telegram update
        context: Telegram context
        callback_prefix: The callback prefix for this filter type
        selected_user_data_key: Key in user_data for storing selected items
        show_function: Function to call to refresh the display
    """
    query = update.callback_query
    if not query or not query.data:
        return

    logger.debug(f"Filter selection callback received: '{query.data}'")
    await query.answer()

    # Extract operation and item name from callback data
    if not query.data.startswith(callback_prefix):
        return

    # Format: {prefix}{operation}__{item_name}__{page}
    callback_suffix = query.data[len(callback_prefix) :]
    parts = callback_suffix.split("__")  # Split on double underscores

    if (
        len(parts) != FILTER_CALLBACK_PARTS
    ):  # Must be exactly operation, item_name, page
        logger.warning(f"Invalid filter callback format: '{callback_suffix}'")
        return

    operation, item_name, page_str = parts

    try:
        current_page = int(page_str)
    except ValueError:
        logger.warning(f"Invalid page number in callback: '{page_str}'")
        return

    if context.user_data is not None:
        selected_items: list[str] = context.user_data.get(selected_user_data_key, [])

        if operation == SearchRecipesFilterOperation.ADD:
            if item_name not in selected_items:
                selected_items.append(item_name)
                logger.debug(f"Added {item_name} to selected {selected_user_data_key}")
        elif operation == SearchRecipesFilterOperation.REMOVE:
            if item_name in selected_items:
                selected_items.remove(item_name)
                logger.debug(
                    f"Removed {item_name} from selected {selected_user_data_key}"
                )
        else:
            logger.warning(f"Unknown operation '{operation}' for '{item_name}'")
            return

        context.user_data[selected_user_data_key] = selected_items

    await show_function(update, context, current_page)

    return True
