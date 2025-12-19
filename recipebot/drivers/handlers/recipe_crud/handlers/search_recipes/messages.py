from telegram.ext import ContextTypes

from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.utils import (
    get_selected_filters,
)

SEARCH_INIT_MESSAGE = (
    "Let's search for recipes! But we need to create a filter first.\n"
    "Would you like to search by category or tag?\n\n"
    "{current_filters}"
    "<i>You can use main keyboard to make another action.</i>"
)

SEARCH_MODE_SELECTION_MESSAGE = (
    "Edit your search filters or execute search\n\n"
    "{current_filters}"
    "<i>You can use main keyboard to make another action.</i>"
)

TAG_SELECTION_MESSAGE = (
    "Select a tag to search for recipes:\n\n"
    "{current_filters}"
    "<i>You can use main keyboard to make another action.</i>"
)

CATEGORY_SELECTION_MESSAGE = (
    "Select categories to filter recipes:\n\n"
    "{current_filters}"
    "<i>You can use main keyboard to make another action.</i>"
)


def _format_filters(tags: list[str], categories: list[str]) -> str:
    """Format tags and categories into a readable string."""
    tag_str = ", ".join([f"#{tag}" for tag in tags]) or "None"
    category_str = (
        ", ".join([f"{category.capitalize()}" for category in categories]) or "None"
    )
    return f"Tags: {tag_str}\nCategories: {category_str}"


def get_current_filters_message(context: ContextTypes.DEFAULT_TYPE) -> str:
    """Get formatted message showing current filters from context."""
    selected_tags, selected_categories = get_selected_filters(context)

    if not selected_tags and not selected_categories:
        return "No filters selected\n\n"

    filters_str = _format_filters(selected_tags, selected_categories)
    return (
        f"Current filters:\n{filters_str}\n\n"
        "Press button with X to remove filter, press button with + to add filter. "
        "Return to mode selection by pressing the button with the back arrow to execute search.\n\n"
    )
