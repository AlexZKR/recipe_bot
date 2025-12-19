"""Tag callback handlers for tag search functionality."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.handler import (
    handle_search_mode_selection,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.handler_context import (
    SearchRecipesCallbackPattern,
    SearchRecipesContextKey,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.tag_search.tag_display import (
    show_tag_selection,
)
from recipebot.drivers.handlers.recipe_crud.shared import (
    parse_pagination_callback,
)

logger = logging.getLogger(__name__)


async def handle_tag_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle tag selection for search."""
    query = update.callback_query
    if not query or not query.data:
        return

    logger.debug(f"Tag selection callback received: '{query.data}'")
    await query.answer()

    # Extract tag name from callback data
    if not query.data.startswith(SearchRecipesCallbackPattern.TAG_PREFIX):
        return

    tag_name = query.data[
        len(SearchRecipesCallbackPattern.TAG_PREFIX) :
    ]  # Remove prefix

    # Store search tag in context for pagination
    if context.user_data is not None:
        context.user_data[SearchRecipesContextKey.SEARCH_TAGS] = [tag_name]

    # Store selected tag in context
    if context.user_data is not None:
        selected_tags: list[str] = context.user_data.get(
            SearchRecipesContextKey.SELECTED_TAGS, []
        )
        if tag_name not in selected_tags:
            selected_tags.append(tag_name)
        context.user_data[SearchRecipesContextKey.SELECTED_TAGS] = selected_tags

    # Go back to mode selection (direct call, not callback)
    await handle_search_mode_selection(update, context)

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
