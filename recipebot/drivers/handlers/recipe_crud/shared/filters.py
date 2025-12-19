"""Shared filter utilities for recipe operations."""

from recipebot.adapters.repositories.sql.recipe.recipe_filters import RecipeFilters


def create_filter_description(filters: RecipeFilters, prefix: str = "with") -> str:
    """Create a human-readable description of applied filters.

    Args:
        filters: The RecipeFilters object containing tag and category filters
        prefix: The word to use before the filter list (e.g., "with", "Filtered by")

    Returns:
        A formatted string describing the filters, or empty string if no filters
    """
    filter_parts = []
    if filters.tag_names:
        filter_parts.append(
            f"tags: {', '.join(f'#{tag}' for tag in filters.tag_names)}"
        )
    if filters.category_names:
        filter_parts.append(f"categories: {', '.join(filters.category_names)}")

    if filter_parts:
        return f" {prefix} {', '.join(filter_parts)}"
    return ""
