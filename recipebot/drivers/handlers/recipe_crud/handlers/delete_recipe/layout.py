from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from recipebot.domain.recipe.recipe import Recipe
from recipebot.drivers.handlers.recipe_crud.shared import (
    create_recipe_selection_keyboard as create_recipe_selection_keyboard_shared,
)

# Backward compatibility alias
create_recipe_selection_keyboard = create_recipe_selection_keyboard_shared


def create_delete_confirmation_keyboard(recipe: Recipe) -> InlineKeyboardMarkup:
    """Create inline keyboard for delete confirmation."""
    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Yes, Delete", callback_data=f"delete_confirm_{recipe.id}_yes"
            )
        ],
        [
            InlineKeyboardButton(
                "❌ No, Cancel", callback_data=f"delete_confirm_{recipe.id}_no"
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)
