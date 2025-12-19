"""Utility functions for search recipes functionality."""

from telegram.ext import ContextTypes

from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.handler_context import (
    SearchRecipesContextKey,
)


def get_selected_filters(
    context: ContextTypes.DEFAULT_TYPE,
) -> tuple[list[str], list[str]]:
    """Extract selected tags and categories from context.

    Returns:
        A tuple of (selected_tags, selected_categories)
    """
    if context.user_data is None:
        return [], []

    selected_tags: list[str] = context.user_data.get(
        SearchRecipesContextKey.SELECTED_TAGS, []
    )
    selected_categories: list[str] = context.user_data.get(
        SearchRecipesContextKey.SELECTED_CATEGORIES, []
    )

    return selected_tags, selected_categories
