"""Shared keyboard creation utilities for recipe CRUD operations."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

from recipebot.domain.recipe.recipe import RecipeCategory


def create_recipe_selection_keyboard(
    recipes, callback_prefix: str
) -> InlineKeyboardMarkup:
    """Create an inline keyboard with recipe names for selection.

    Args:
        recipes: List of Recipe objects
        callback_prefix: Prefix for callback data (e.g., 'recipe_', 'edit_recipe_')

    Returns:
        InlineKeyboardMarkup with recipe buttons
    """
    keyboard = []
    for recipe in recipes:
        keyboard.append(
            [
                InlineKeyboardButton(
                    recipe.title, callback_data=f"{callback_prefix}{recipe.id}"
                )
            ]
        )

    return InlineKeyboardMarkup(keyboard)


def create_category_reply_keyboard() -> ReplyKeyboardMarkup:
    """Create reply keyboard for category selection (used in recipe creation)."""
    reply_keyboard = [[category.value for category in RecipeCategory]]
    return ReplyKeyboardMarkup(
        reply_keyboard,
        selective=True,
        one_time_keyboard=True,
        input_field_placeholder="Recipe category",
    )
