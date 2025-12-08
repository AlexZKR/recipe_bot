from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from recipebot.domain.recipe.recipe import Recipe


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
