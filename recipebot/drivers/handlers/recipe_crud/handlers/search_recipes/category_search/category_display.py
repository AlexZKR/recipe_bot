"""Category display utilities for category search functionality."""

from telegram import Update
from telegram.ext import ContextTypes

from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.category_search.category_filter_profile import (
    category_filter_profile,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.filter_selection_utils import (
    show_generic_filter_selection,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.messages import (
    CATEGORY_SELECTION_MESSAGE,
    get_current_filters_message,
)


async def show_category_selection(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    page: int = 1,
):
    """Show paginated list of available categories for search."""
    # Create message with current filters info
    current_filters = get_current_filters_message(context)
    message = CATEGORY_SELECTION_MESSAGE.format(current_filters=current_filters)

    await show_generic_filter_selection(
        update=update,
        context=context,
        profile=category_filter_profile,
        page=page,
        edit_message=True,  # Always edit messages when possible
        message_template=message,
    )
