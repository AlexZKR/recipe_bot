from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from recipebot.domain.recipe.recipe import Recipe, RecipeCategory
from recipebot.drivers.handlers.main_keyboard import MAIN_KEYBOARD
from recipebot.drivers.handlers.recipe_crud.handlers.edit_recipe.constants import (
    EDIT_FIELD_MIN_PARTS,
    EDIT_RECIPE_PREFIX,
    EDITING_CATEGORY,
    EDITING_DESCRIPTION,
    EDITING_INGREDIENTS,
    EDITING_LINK,
    EDITING_NOTES,
    EDITING_SERVINGS,
    EDITING_STEPS,
    EDITING_TIME,
    EDITING_TITLE,
)
from recipebot.drivers.handlers.recipe_crud.handlers.edit_recipe.handler_context import (
    EditRecipeContextKey,
)
from recipebot.drivers.handlers.recipe_crud.shared.callbacks import (
    parse_prefixed_callback,
)
from recipebot.drivers.state import get_state


def parse_edit_recipe_callback(callback_data: str | None) -> str | None:
    """Parse edit recipe callback data.

    Args:
        callback_data: Callback data in format "edit_recipe_{recipe_id}"

    Returns:
        recipe_id string or None if invalid
    """
    return parse_prefixed_callback(callback_data, EDIT_RECIPE_PREFIX)


def parse_edit_field_callback(callback_data: str) -> tuple[str, str] | None:
    """Parse edit field callback data.

    Args:
        callback_data: Callback data in format "edit_field_{recipe_id}_{field_name}"

    Returns:
        Tuple of (recipe_id, field_name) or None if invalid
    """
    if not callback_data or not callback_data.startswith("edit_field_"):
        return None

    parts = callback_data.split("_")
    if len(parts) < EDIT_FIELD_MIN_PARTS:
        return None

    recipe_id = parts[2]
    field_name = parts[3]

    return recipe_id, field_name


def validate_and_convert_field_value(field_name: str, value: str) -> str | int:
    """Validate and convert field values.

    Args:
        field_name: Name of the field being edited
        value: Raw input value

    Returns:
        Converted value appropriate for the field type

    Raises:
        ValueError: If validation fails
    """
    if field_name == "category":
        return RecipeCategory(value or "").value
    elif field_name == "servings" and value:
        return int(value)
    else:
        # String fields - keep as is
        return value


def start_field_editing(context, recipe_id: str, field_name: str) -> int:
    """Helper function to start editing a specific field. Returns the appropriate conversation state."""

    # Store field in context for the conversation (recipe object already stored)
    context.user_data[EditRecipeContextKey.EDITING_FIELD] = field_name

    # Return appropriate conversation state
    state_mapping = {
        "title": EDITING_TITLE,
        "ingredients": EDITING_INGREDIENTS,
        "steps": EDITING_STEPS,
        "category": EDITING_CATEGORY,
        "servings": EDITING_SERVINGS,
        "description": EDITING_DESCRIPTION,
        "estimated_time": EDITING_TIME,
        "notes": EDITING_NOTES,
        "link": EDITING_LINK,
    }

    return state_mapping.get(field_name, EDITING_TITLE)


async def save_field_value(update: Update, context: ContextTypes.DEFAULT_TYPE, state):
    """Save the field value and finish editing."""
    if not update.message or not context.user_data:
        return ConversationHandler.END

    # Get the recipe and field info from context
    recipe = context.user_data.get(EditRecipeContextKey.EDITING_RECIPE)
    field_name = context.user_data.get(EditRecipeContextKey.EDITING_FIELD)

    if not recipe or not field_name:
        await update.message.reply_text(
            "Recipe or field information missing from session. Please start over."
        )
        return ConversationHandler.END

    # Get the new value
    raw_value = update.message.text
    if raw_value is None:
        await update.message.reply_text("Please provide a value.")
        return state  # Stay in same state to retry

    # Validate and convert values as needed
    try:
        new_value = validate_and_convert_field_value(field_name, raw_value)
    except (ValueError, AttributeError) as e:
        await update.message.reply_text(f"Invalid value: {str(e)}")
        return state  # Stay in same state to retry

    # Update the field in the recipe object
    setattr(recipe, field_name, new_value)

    # Save back to database
    recipe_repo = get_state(context)["recipe_repo"]
    try:
        await recipe_repo.update(recipe)
    except ValueError as e:
        await update.message.reply_text(f"Error updating recipe: {str(e)}")
        return ConversationHandler.END

    await update.message.reply_text(
        f"✅ {field_name.title()} updated successfully!", reply_markup=MAIN_KEYBOARD
    )

    # Clear user data
    if context.user_data:
        context.user_data.clear()

    return ConversationHandler.END


def create_field_edit_prompt(recipe: Recipe, field_name: str) -> str:
    """Create a prompt message for editing a specific field."""
    current_value = getattr(recipe, field_name, "")
    if current_value is None:
        current_value = ""

    field_prompts = {
        "title": f"Current title: **{current_value}**\n\nEnter new title:",
        "ingredients": f"Current ingredients:\n{current_value}\n\nEnter new ingredients:",
        "steps": f"Current steps:\n{current_value}\n\nEnter new steps:",
        "servings": f"Current servings: **{current_value or 'Not specified'}**\n\nEnter number of servings:",
        "description": f"Current description: **{current_value or 'No description'}**\n\nEnter new description:",
        "estimated_time": f"Current time: **{current_value or 'Not specified'}**\n\nEnter estimated time:",
        "notes": f"Current notes: **{current_value or 'No notes'}**\n\nEnter new notes:",
        "link": f"Current link: **{current_value or 'No link'}**\n\nEnter new link:",
    }

    return field_prompts.get(field_name, f"Enter new {field_name}:")
