"""Category display utilities for category search functionality."""

from telegram import Update
from telegram.ext import ContextTypes

from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.category_search.category_filter_profile import (
    category_filter_profile,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.filter_selection_utils import (
    show_generic_filter_selection,
)


async def show_category_selection(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    page: int = 1,
):
    """Show paginated list of available categories for search."""
    # Create message with current filters info
    # For categories, we'll use a generic message since categories don't have custom messages like tags
    selected_categories = (
        context.user_data.get(category_filter_profile.selected_user_data_key, [])
        if context.user_data
        else []
    )

    filters_text = (
        f"Selected categories: {', '.join(selected_categories)}"
        if selected_categories
        else "No categories selected yet."
    )
    message = f"Select categories to filter recipes:\n\n{filters_text}"

    await show_generic_filter_selection(
        update=update,
        context=context,
        profile=category_filter_profile,
        page=page,
        edit_message=True,  # Always edit messages when possible
        message_template=message,
    )
