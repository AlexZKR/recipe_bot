"""Tag callback handlers for tag search functionality."""

from telegram import Update
from telegram.ext import ContextTypes

from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.filter_selection_utils import (
    handle_generic_filter_pagination,
    handle_generic_filter_selection,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.handler_context import (
    SearchRecipesCallbackPattern,
    SearchRecipesContextKey,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.tag_search.tag_display import (
    show_tag_selection,
)


async def handle_tag_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle tag selection for search (add/remove tags)."""
    return await handle_generic_filter_selection(
        update=update,
        context=context,
        callback_prefix=SearchRecipesCallbackPattern.TAG_PREFIX,
        selected_user_data_key=SearchRecipesContextKey.SELECTED_TAGS,
        show_function=show_tag_selection,
    )


async def handle_tag_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle pagination navigation for tag selection."""
    return await handle_generic_filter_pagination(
        update=update,
        context=context,
        page_prefix=SearchRecipesCallbackPattern.TAG_PAGE_PREFIX,
        show_function=show_tag_selection,
    )
