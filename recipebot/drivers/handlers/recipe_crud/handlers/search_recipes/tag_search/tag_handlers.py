"""Tag callback handlers for tag search functionality."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.handler_context import (
    SearchRecipesCallbackPattern,
    SearchRecipesContextKey,
    SearchRecipesFilterOperation,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.tag_search.tag_display import (
    show_tag_selection,
)
from recipebot.drivers.handlers.recipe_crud.shared import (
    parse_pagination_callback,
)

logger = logging.getLogger(__name__)

FILTER_CALLBACK_PARTS = 3


async def handle_tag_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle tag selection for search (add/remove tags)."""
    query = update.callback_query
    if not query or not query.data:
        return

    logger.debug(f"Tag selection callback received: '{query.data}'")
    await query.answer()

    # Extract operation and tag name from callback data
    if not query.data.startswith(SearchRecipesCallbackPattern.TAG_PREFIX):
        return

    # Format: search_tag_{operation}__{tag_name}__{page}
    callback_suffix = query.data[len(SearchRecipesCallbackPattern.TAG_PREFIX) :]
    parts = callback_suffix.split("__")  # Split on double underscores

    if len(parts) != FILTER_CALLBACK_PARTS:  # Must be exactly operation, tag_name, page
        logger.warning(f"Invalid tag callback format: '{callback_suffix}'")
        return

    operation, tag_name, page_str = parts

    try:
        current_page = int(page_str)
    except ValueError:
        logger.warning(f"Invalid page number in callback: '{page_str}'")
        return

    if context.user_data is not None:
        selected_tags: list[str] = context.user_data.get(
            SearchRecipesContextKey.SELECTED_TAGS, []
        )

        if operation == SearchRecipesFilterOperation.ADD:
            # Add tag if not already selected
            if tag_name not in selected_tags:
                selected_tags.append(tag_name)
                logger.debug(f"Added tag '{tag_name}' to selected tags")
        elif operation == SearchRecipesFilterOperation.REMOVE:
            # Remove tag if it exists
            if tag_name in selected_tags:
                selected_tags.remove(tag_name)
                logger.debug(f"Removed tag '{tag_name}' from selected tags")
        else:
            logger.warning(f"Unknown operation '{operation}' for tag '{tag_name}'")
            return

        context.user_data[SearchRecipesContextKey.SELECTED_TAGS] = selected_tags

    await show_tag_selection(update, context, page=current_page, edit_message=True)

    # Return True to indicate we handled this callback
    return True


async def handle_tag_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle pagination navigation for tag selection."""
    query = update.callback_query
    if not query or not query.data:
        return

    await query.answer()

    # Parse pagination callback
    page = parse_pagination_callback(
        query.data, SearchRecipesCallbackPattern.TAG_PAGE_PREFIX
    )
    if page is None:
        return

    # Show the requested page
    await show_tag_selection(update, context, page=page, edit_message=True)

    # Return True to indicate we handled this callback
    return True
