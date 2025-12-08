from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from recipebot.domain.recipe.recipe import Recipe, RecipeCategory


def create_category_selection_keyboard(recipe_id: str) -> InlineKeyboardMarkup:
    """Create inline keyboard for category selection (used in recipe editing).

    Args:
        recipe_id: The ID of the recipe being edited

    Returns:
        InlineKeyboardMarkup with category buttons
    """
    keyboard = []
    for category in RecipeCategory:
        keyboard.append(
            [
                InlineKeyboardButton(
                    f"📊 {category.value}",
                    callback_data=f"edit_category_{recipe_id}_{category.value}",
                )
            ]
        )

    return InlineKeyboardMarkup(keyboard)


def create_field_selection_keyboard(recipe: Recipe) -> InlineKeyboardMarkup:
    """Create inline keyboard for field selection during editing."""
    keyboard = [
        [
            InlineKeyboardButton(
                "📝 Title", callback_data=f"edit_field_{recipe.id}_title"
            )
        ],
        [
            InlineKeyboardButton(
                "🍳 Ingredients", callback_data=f"edit_field_{recipe.id}_ingredients"
            )
        ],
        [
            InlineKeyboardButton(
                "👨‍🍳 Steps", callback_data=f"edit_field_{recipe.id}_steps"
            )
        ],
        [
            InlineKeyboardButton(
                "📊 Category", callback_data=f"edit_field_{recipe.id}_category"
            )
        ],
        [
            InlineKeyboardButton(
                "🍽️ Servings", callback_data=f"edit_field_{recipe.id}_servings"
            )
        ],
        [
            InlineKeyboardButton(
                "📝 Description", callback_data=f"edit_field_{recipe.id}_description"
            )
        ],
        [
            InlineKeyboardButton(
                "⏱️ Time", callback_data=f"edit_field_{recipe.id}_estimated_time"
            )
        ],
        [
            InlineKeyboardButton(
                "📌 Notes", callback_data=f"edit_field_{recipe.id}_notes"
            )
        ],
        [InlineKeyboardButton("🔗 Link", callback_data=f"edit_field_{recipe.id}_link")],
    ]

    return InlineKeyboardMarkup(keyboard)
