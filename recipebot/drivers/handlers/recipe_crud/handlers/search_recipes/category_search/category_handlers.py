"""Category callback handlers for category search functionality."""

from telegram import Update
from telegram.ext import ContextTypes

from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.category_search.category_constants import (
    CATEGORY_PAGE_PREFIX,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.category_search.category_display import (
    show_category_selection,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.category_search.category_filter_profile import (
    category_filter_profile,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.filter_selection_utils import (
    handle_generic_filter_pagination,
    handle_generic_filter_selection,
)


async def handle_category_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle category selection for search (add/remove categories)."""
    return await handle_generic_filter_selection(
        update=update,
        context=context,
        profile=category_filter_profile,
        show_function=show_category_selection,
    )


async def handle_category_pagination(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Handle pagination navigation for category selection."""
    return await handle_generic_filter_pagination(
        update=update,
        context=context,
        page_prefix=CATEGORY_PAGE_PREFIX,
        show_function=show_category_selection,
    )
