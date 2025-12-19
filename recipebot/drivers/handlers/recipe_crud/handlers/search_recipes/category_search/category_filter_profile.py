"""Category-specific filter profile configuration."""

from recipebot.domain.recipe.recipe import RecipeCategory
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.category_search.category_constants import (
    CATEGORY_ITEM_TYPE,
    CATEGORY_PAGE_PREFIX,
    CATEGORY_PREFIX,
    SELECTED_CATEGORIES_KEY,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.filter_selection_utils.filter_profile import (
    FilterProfile,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.handler_context import (
    SearchRecipesCallbackPattern,
)


async def get_available_categories(user_id: int) -> list[RecipeCategory]:
    """Get all available recipe categories."""
    return list[RecipeCategory](RecipeCategory)


# Create the category filter profile instance
category_filter_profile = FilterProfile(
    item_getter=get_available_categories,
    selected_user_data_key=SELECTED_CATEGORIES_KEY,
    callback_prefix=CATEGORY_PREFIX,
    page_prefix=CATEGORY_PAGE_PREFIX,
    item_type=CATEGORY_ITEM_TYPE,
    back_callback_data=SearchRecipesCallbackPattern.MODE_PREFIX,
)
