from types import SimpleNamespace
from uuid import UUID

from telegram import Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from recipebot.drivers.handlers.main_keyboard import MAIN_KEYBOARD
from recipebot.drivers.handlers.recipe_crud.handlers.delete_recipe.handler_context import (
    DeleteRecipeContextKey,
)
from recipebot.drivers.handlers.recipe_crud.handlers.delete_recipe.layout import (
    create_delete_confirmation_keyboard,
)
from recipebot.drivers.handlers.recipe_crud.handlers.delete_recipe.utils import (
    parse_delete_confirm_callback,
    parse_delete_recipe_callback,
)
from recipebot.drivers.handlers.recipe_crud.shared import (
    PaginatedResult,
    create_paginated_keyboard,
    parse_pagination_callback,
)
from recipebot.drivers.state import get_state
from recipebot.ports.repositories.exceptions import RecipeNotFound


async def delete_recipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _show_delete_recipe_list(update, context, page=1)


async def _show_delete_recipe_list(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    page: int = 1,
    edit_message: bool = False,
):
    """Show paginated recipe list for deletion."""
    if not update.effective_chat or not update.effective_user:
        raise Exception("Not chat or user in the update")

    recipe_repo = get_state(context)["recipe_repo"]
    recipes = await recipe_repo.list_by_user(update.effective_user.id)

    if not recipes:
        if edit_message and update.callback_query:
            await update.callback_query.edit_message_text(
                "You don't have any recipes yet. Use /add to create your first recipe!"
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="You don't have any recipes yet. Use /add to create your first recipe!",
            )
        return

    # Create paginated result
    paginated_result = PaginatedResult(recipes, page, callback_prefix="delete_recipe_")

    # Create paginated keyboard
    def item_callback_factory(recipe, current_page):
        return f"delete_recipe_{recipe.id}"

    reply_markup = create_paginated_keyboard(
        paginated_result, item_callback_factory, navigation_prefix="delete_page"
    )

    message_text = (
        f"Select a recipe to delete:\n\n{paginated_result.get_page_info_text()}"
    )

    if edit_message and update.callback_query:
        await update.callback_query.edit_message_text(
            message_text,
            reply_markup=reply_markup,
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message_text,
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

    # Show paginated recipe selection by directly calling the pagination display
    # Create a simple update-like object
    mock_update = SimpleNamespace()
    mock_update.callback_query = query
    mock_update.effective_chat = query.message.chat if query.message else None
    mock_update.effective_user = query.from_user

    # Show paginated recipe selection
    await _show_delete_recipe_list(mock_update, context, page=1, edit_message=True)  # type: ignore


async def handle_delete_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle pagination navigation for delete operations."""
    query = update.callback_query
    if not query or not query.data:
        return

    await query.answer()

    # Parse pagination callback
    page = parse_pagination_callback(query.data, "delete_page")
    if page is None:
        return

    # Show the requested page
    await _show_delete_recipe_list(update, context, page=page, edit_message=True)


# Handlers
delete_recipe_handler = CommandHandler("delete_recipe", delete_recipe)
delete_recipe_selection_handler = CallbackQueryHandler(
    handle_recipe_selection_for_delete, pattern=r"^delete_recipe_"
)
delete_pagination_handler = CallbackQueryHandler(
    handle_delete_pagination, pattern=r"^delete_page_"
)
delete_confirmation_handler = CallbackQueryHandler(
    handle_delete_confirmation, pattern=r"^delete_confirm_"
)
