from uuid import UUID

from telegram import Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from recipebot.drivers.handlers.main_keyboard import MAIN_KEYBOARD
from recipebot.drivers.handlers.recipe.delete_recipe.handler_context import (
    DeleteRecipeContextKey,
)
from recipebot.drivers.handlers.recipe.delete_recipe.layout import (
    create_delete_confirmation_keyboard,
)
from recipebot.drivers.handlers.recipe.delete_recipe.utils import (
    parse_delete_confirm_callback,
    parse_delete_recipe_callback,
)
from recipebot.drivers.handlers.recipe.list_recipes_handler import (
    create_recipe_selection_keyboard,
)
from recipebot.drivers.state import get_state
from recipebot.ports.repositories.exceptions import RecipeNotFound


async def delete_recipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the recipe deletion process by showing recipe selection."""
    if not update.effective_chat or not update.effective_user:
        raise Exception("Not chat or user in the update")

    recipe_repo = get_state(context)["recipe_repo"]
    recipes = await recipe_repo.list_by_user(update.effective_user.id)

    if not recipes:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="You don't have any recipes yet. Use /add to create your first recipe!",
        )
        return

    # Create inline keyboard with recipe names for deletion
    reply_markup = create_recipe_selection_keyboard(recipes, "delete_recipe_")

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Select a recipe to delete:",
        reply_markup=reply_markup,
    )

    # Also show the main keyboard below
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Or use the keyboard below:",
        reply_markup=MAIN_KEYBOARD,
    )


async def handle_recipe_selection_for_delete(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Handle recipe selection for deletion - show confirmation."""
    query = update.callback_query
    if not query or not query.message or not query.message.chat:
        return

    await query.answer()

    # Extract recipe ID from callback data
    recipe_id = parse_delete_recipe_callback(query.data)
    if not recipe_id:
        return

    # Get recipe details to show current values
    recipe_repo = get_state(context)["recipe_repo"]
    try:
        recipe = await recipe_repo.get(UUID(recipe_id))
    except RecipeNotFound:
        await query.edit_message_text("Recipe not found.")
        return

    # Store recipe in user context for deletion
    if context.user_data is None:
        context.user_data = {}
    context.user_data[DeleteRecipeContextKey.RECIPE_TO_DELETE] = recipe

    # Create confirmation keyboard
    reply_markup = create_delete_confirmation_keyboard(recipe)

    await query.edit_message_text(
        f"Do you really want to delete this recipe?\n\n"
        f"**{recipe.title}**\n\n"
        f"⚠️ This action cannot be undone!",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def handle_delete_confirmation(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Handle delete confirmation (yes/no)."""
    query = update.callback_query
    if not query or not query.message or not query.message.chat:
        return

    await query.answer()

    # Parse confirmation callback
    parsed = parse_delete_confirm_callback(query.data)
    if not parsed:
        return

    recipe_id, choice = parsed

    if choice == "no":
        # User cancelled, go back to recipe selection
        await _return_to_recipe_selection(query, context)
        return

    # User confirmed deletion
    recipe = (
        context.user_data.get(DeleteRecipeContextKey.RECIPE_TO_DELETE)
        if context.user_data
        else None
    )

    if not recipe:
        await query.edit_message_text("Recipe not found in session. Please start over.")
        return

    # Delete the recipe
    recipe_repo = get_state(context)["recipe_repo"]
    user_id = query.from_user.id if query.from_user else None
    if not user_id:
        await query.edit_message_text("User not found.")
        return

    try:
        await recipe_repo.delete(UUID(recipe_id), user_id)
    except RecipeNotFound:
        await query.edit_message_text("Recipe not found or access denied.")
        return

    # Clear context and show success
    if context.user_data:
        context.user_data.pop(DeleteRecipeContextKey.RECIPE_TO_DELETE, None)

    await query.edit_message_text(
        f"✅ Recipe **{recipe.title}** has been deleted successfully!",
        reply_markup=None,
        parse_mode="Markdown",
    )

    # Send the main keyboard
    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text="What would you like to do next?",
        reply_markup=MAIN_KEYBOARD,
    )


async def _return_to_recipe_selection(query, context: ContextTypes.DEFAULT_TYPE):
    """Helper function to return to recipe selection after cancellation."""
    if not context.user_data:
        return

    # Clear the recipe to delete from context
    context.user_data.pop(DeleteRecipeContextKey.RECIPE_TO_DELETE, None)

    # Get user's recipes again
    user_id = query.from_user.id if query.from_user else None
    if not user_id:
        return

    recipe_repo = get_state(context)["recipe_repo"]
    recipes = await recipe_repo.list_by_user(user_id)

    if not recipes:
        await query.edit_message_text(
            "You don't have any recipes left. Use /add to create a new recipe!",
            reply_markup=MAIN_KEYBOARD,
        )
        return

    # Show recipe selection again
    reply_markup = create_recipe_selection_keyboard(recipes, "delete_recipe_")
    await query.edit_message_text(
        "Select a recipe to delete:",
        reply_markup=reply_markup,
    )


# Handlers
delete_recipe_handler = CommandHandler("delete_recipe", delete_recipe)
delete_recipe_selection_handler = CallbackQueryHandler(
    handle_recipe_selection_for_delete, pattern=r"^delete_recipe_"
)
delete_confirmation_handler = CallbackQueryHandler(
    handle_delete_confirmation, pattern=r"^delete_confirm_"
)
