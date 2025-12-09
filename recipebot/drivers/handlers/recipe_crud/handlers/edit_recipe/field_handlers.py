"""Field-specific save handlers for edit recipe functionality."""

from telegram import Update
from telegram.ext import ContextTypes

from recipebot.drivers.handlers.recipe_crud.handlers.edit_recipe.constants import (
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
from recipebot.drivers.handlers.recipe_crud.handlers.edit_recipe.utils import (
    save_field_value,
)


async def save_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save the title field."""
    print("DEBUG: save_title called")  # Debug
    return await save_field_value(update, context, EDITING_TITLE)


async def save_ingredients(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save the ingredients field."""
    return await save_field_value(update, context, EDITING_INGREDIENTS)


async def save_steps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save the steps field."""
    return await save_field_value(update, context, EDITING_STEPS)


async def save_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save the category field."""
    return await save_field_value(update, context, EDITING_CATEGORY)


async def save_servings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save the servings field."""
    return await save_field_value(update, context, EDITING_SERVINGS)


async def save_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save the description field."""
    return await save_field_value(update, context, EDITING_DESCRIPTION)


async def save_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save the estimated time field."""
    return await save_field_value(update, context, EDITING_TIME)


async def save_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save the notes field."""
    return await save_field_value(update, context, EDITING_NOTES)


async def save_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save the link field."""
    return await save_field_value(update, context, EDITING_LINK)
