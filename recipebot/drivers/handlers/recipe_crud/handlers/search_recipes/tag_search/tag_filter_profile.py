"""Tag-specific filter profile configuration."""

from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.filter_selection_utils.filter_profile import (
    FilterProfile,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.handler_context import (
    SearchRecipesCallbackPattern,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.tag_search.tag_constants import (
    SELECTED_TAGS_KEY,
    TAG_ITEM_TYPE,
    TAG_PAGE_PREFIX,
    TAG_PREFIX,
)
from recipebot.drivers.state import get_state


async def get_user_tags(user_id: int) -> list:
    """Get user's tags from repository."""
    recipe_repo = get_state()["recipe_repo"]
    return await recipe_repo.get_user_tags(user_id)


tag_filter_profile = FilterProfile(
    item_getter=get_user_tags,
    selected_user_data_key=SELECTED_TAGS_KEY,
    callback_prefix=TAG_PREFIX,
    page_prefix=TAG_PAGE_PREFIX,
    item_type=TAG_ITEM_TYPE,
    back_callback_data=SearchRecipesCallbackPattern.MODE_PREFIX,
    show_main_keyboard=True,
)
