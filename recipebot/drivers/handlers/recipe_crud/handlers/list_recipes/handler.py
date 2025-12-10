from uuid import UUID

from telegram import Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from recipebot.drivers.handlers.main_keyboard import MAIN_KEYBOARD
from recipebot.drivers.handlers.recipe_crud.handlers.list_recipes.utils import (
    parse_recipe_callback,
)
from recipebot.drivers.handlers.recipe_crud.shared import (
    PaginatedResult,
    create_paginated_keyboard,
    parse_pagination_callback,
)
from recipebot.drivers.state import get_state
from recipebot.ports.repositories.exceptions import RecipeNotFound


async def list_recipes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _show_recipe_list(update, context, page=1)


async def _show_recipe_list(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    page: int = 1,
    edit_message: bool = False,
):
    """Show paginated recipe list."""
    if not update.effective_chat or not update.effective_user:
        raise Exception("Not chat or user in the update")

    recipe_repo = get_state()["recipe_repo"]
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
    paginated_result = PaginatedResult(recipes, page, callback_prefix="recipe_")

    # Create paginated keyboard
    def item_callback_factory(recipe, current_page):
        return f"recipe_{recipe.id}"

    reply_markup = create_paginated_keyboard(
        paginated_result, item_callback_factory, navigation_prefix="list_page"
    )

    message_text = (
        f"Select a recipe to view:\n\n{paginated_result.get_page_info_text()}"
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


async def handle_recipe_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query or not query.message or not query.message.chat:
        return

    await query.answer()

    # Extract recipe ID from callback data
    recipe_id = parse_recipe_callback(query.data)
    if not recipe_id:
        await query.edit_message_text("Invalid recipe selection.")
        return

    # Get recipe details
    recipe_repo = get_state()["recipe_repo"]
    try:
        recipe = await recipe_repo.get(UUID(recipe_id))
    except RecipeNotFound:
        await query.edit_message_text("Recipe not found.")
        return

    # Format recipe details
    recipe_text = recipe.to_md()

    await query.edit_message_text(recipe_text)

    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text="What would you like to do next?",
        reply_markup=MAIN_KEYBOARD,
    )


async def handle_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle pagination navigation."""
    query = update.callback_query
    if not query or not query.data:
        return

    await query.answer()

    # Parse pagination callback
    page = parse_pagination_callback(query.data, "list_page")
    if page is None:
        return

    # Show the requested page
    await _show_recipe_list(update, context, page=page, edit_message=True)


list_recipes_handler = CommandHandler("list", list_recipes)
recipe_selection_handler = CallbackQueryHandler(
    handle_recipe_selection, pattern=r"^recipe_"
)
list_pagination_handler = CallbackQueryHandler(
    handle_pagination, pattern=r"^list_page_"
)
