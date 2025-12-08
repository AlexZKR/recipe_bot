from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from recipebot.domain.recipe.recipe import Recipe, RecipeCategory


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


def create_field_edit_prompt(recipe: Recipe, field_name: str) -> str:
    """Create a prompt message for editing a specific field."""
    current_value = getattr(recipe, field_name, "")
    if current_value is None:
        current_value = ""

    field_prompts = {
        "title": f"Current title: **{current_value}**\n\nEnter new title:",
        "ingredients": f"Current ingredients:\n{current_value}\n\nEnter new ingredients:",
        "steps": f"Current steps:\n{current_value}\n\nEnter new steps:",
        "category": f"Current category: **{current_value}**\n\nChoose from: {', '.join([cat.value for cat in RecipeCategory])}",
        "servings": f"Current servings: **{current_value or 'Not specified'}**\n\nEnter number of servings:",
        "description": f"Current description: **{current_value or 'No description'}**\n\nEnter new description:",
        "estimated_time": f"Current time: **{current_value or 'Not specified'}**\n\nEnter estimated time:",
        "notes": f"Current notes: **{current_value or 'No notes'}**\n\nEnter new notes:",
        "link": f"Current link: **{current_value or 'No link'}**\n\nEnter new link:",
    }

    return field_prompts.get(field_name, f"Enter new {field_name}:")
