"""Tag display utilities for tag search functionality."""

from telegram import Update
from telegram.ext import ContextTypes

from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.filter_selection_utils import (
    show_generic_filter_selection,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.messages import (
    TAG_SELECTION_MESSAGE,
    get_current_filters_message,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.tag_search.tag_filter_profile import (
    tag_filter_profile,
)


async def show_tag_selection(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    page: int = 1,
):
    """Show paginated list of available tags for search."""
    # Create message with current filters info
    current_filters = get_current_filters_message(context)
    message = TAG_SELECTION_MESSAGE.format(current_filters=current_filters)

    await show_generic_filter_selection(
        update=update,
        context=context,
        profile=tag_filter_profile,
        page=page,
        message_template=message,
    )
