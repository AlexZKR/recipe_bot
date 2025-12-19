"""Tag display utilities for tag search functionality."""

from telegram import Update
from telegram.ext import ContextTypes

from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.filter_selection_utils import (
    show_generic_filter_selection,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.handler_context import (
    SearchRecipesCallbackPattern,
    SearchRecipesContextKey,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.messages import (
    TAG_SELECTION_MESSAGE,
    get_current_filters_message,
)
from recipebot.drivers.state import get_state


async def get_user_tags(user_id: int) -> list:
    """Get user's tags from repository."""
    recipe_repo = get_state()["recipe_repo"]
    return await recipe_repo.get_user_tags(user_id)


async def show_tag_selection(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    page: int = 1,
    edit_message: bool = True,
):
    """Show paginated list of available tags for search."""
    # Create message with current filters info
    current_filters = get_current_filters_message(context)
    message = TAG_SELECTION_MESSAGE.format(current_filters=current_filters)

    await show_generic_filter_selection(
        update=update,
        context=context,
        item_getter=get_user_tags,
        selected_user_data_key=SearchRecipesContextKey.SELECTED_TAGS,
        callback_prefix=SearchRecipesCallbackPattern.TAG_PREFIX,
        page_prefix=SearchRecipesCallbackPattern.TAG_PAGE_PREFIX,
        item_type="tags",
        back_callback_data=SearchRecipesCallbackPattern.MODE_PREFIX,
        page=page,
        edit_message=edit_message,
        show_main_keyboard=True,
        message_template=message,
    )
