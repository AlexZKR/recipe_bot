from telegram.ext import ContextTypes

from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.handler_context import (
    SearchRecipesContextKey,
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


def get_current_filters_message(context: ContextTypes.DEFAULT_TYPE) -> str:
    if context.user_data is None:
        return "No filters selected\n\n"
    selected_tags: list[str] = context.user_data.get(
        SearchRecipesContextKey.SELECTED_TAGS, []
    )
    selected_categories: list[str] = context.user_data.get(
        SearchRecipesContextKey.SELECTED_CATEGORIES, []
    )
    return (
        f"Current filters:\n"
        f"Tags: {', '.join([f'#{tag}' for tag in selected_tags]) or 'None'}\n"
        f"Categories: {', '.join([f'{category.capitalize()}' for category in selected_categories]) or 'None'}\n\n"
        "Press button with X to remove filter, press button with + to add filter. Return to mode selection by pressing the button with the back arrow to execute search.\n\n"
    )
