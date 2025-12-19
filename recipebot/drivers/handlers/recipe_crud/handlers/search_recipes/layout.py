from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.handler_context import (
    SearchRecipesCallbackPattern,
    SearchRecipesMode,
)


def create_search_mode_keyboard() -> InlineKeyboardMarkup:
    """Create inline keyboard for search mode selection."""
    keyboard = [
        [
            InlineKeyboardButton(
                "By Category",
                callback_data=f"{SearchRecipesCallbackPattern.MODE_PREFIX}{SearchRecipesMode.CATEGORY}",
            )
        ],
        [
            InlineKeyboardButton(
                "By Tag",
                callback_data=f"{SearchRecipesCallbackPattern.MODE_PREFIX}{SearchRecipesMode.TAG}",
            )
        ],
        [
            InlineKeyboardButton(
                "🔍 Search",
                callback_data=SearchRecipesCallbackPattern.SEARCH_PREFIX,
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)
