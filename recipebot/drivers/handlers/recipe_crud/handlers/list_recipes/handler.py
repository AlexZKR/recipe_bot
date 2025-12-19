from uuid import UUID

from telegram import Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from recipebot.adapters.repositories.sql.recipe.recipe_filters import RecipeFilters
from recipebot.drivers.handlers.auth.decorators import only_registered
from recipebot.drivers.handlers.main_keyboard import MAIN_KEYBOARD
from recipebot.drivers.handlers.recipe_crud.handlers.list_recipes.utils import (
    parse_recipe_callback,
)
from recipebot.drivers.handlers.recipe_crud.shared import (
    PaginatedResult,
    create_filter_description,
    create_paginated_keyboard,
    parse_pagination_callback,
)
from recipebot.drivers.state import get_state
from recipebot.ports.repositories.exceptions import RecipeNotFound


@only_registered
async def list_recipes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _show_recipe_list(update, context, page=1)


async def _show_recipe_list(  # noqa: PLR0912
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    page: int = 1,
    edit_message: bool = False,
    filters: RecipeFilters | None = None,
):
    """Show paginated recipe list."""
    if not update.effective_chat or not update.effective_user:
        raise Exception("Not chat or user in the update")

    recipe_repo = get_state()["recipe_repo"]
    if filters is None:
        filters = RecipeFilters(user_id=update.effective_user.id)
    recipes = await recipe_repo.list_filtered(filters)

    if not recipes:
        filter_desc = create_filter_description(filters)
        message = f"No recipes found{filter_desc}. Try adjusting your filters or use /add to create a new recipe!"

        if edit_message and update.callback_query:
            await update.callback_query.edit_message_text(message)
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
            )
        return

    # Create paginated result
    paginated_result = PaginatedResult(recipes, page)

    # Create paginated keyboard
    def item_callback_factory(recipe, current_page):
        return f"recipe_{recipe.id}"

    reply_markup = create_paginated_keyboard(
        paginated_result, item_callback_factory, navigation_prefix="list_page"
    )

    # Create filter description for the header
    filter_desc = create_filter_description(filters, prefix="Filtered by")
    if filter_desc:
        filter_desc += "\n\n"

    message_text = f"{filter_desc}Select a recipe to view:\n\n{paginated_result.get_page_info_text()}"

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
