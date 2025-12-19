from uuid import UUID

from telegram import Update
from telegram.ext import ContextTypes

from recipebot.adapters.repositories.sql.recipe.recipe_filters import RecipeFilters
from recipebot.drivers.handlers.main_keyboard import MAIN_KEYBOARD
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.handler_context import (
    SearchRecipesCallbackPattern,
    SearchRecipesContextKey,
)
from recipebot.drivers.handlers.recipe_crud.shared import (
    PaginatedResult,
    create_paginated_keyboard,
    parse_pagination_callback,
)
from recipebot.drivers.state import get_state
from recipebot.ports.repositories.exceptions import RecipeNotFound


async def _show_search_results(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    search_tags: list[str],
    page: int = 1,
    edit_message: bool = False,
):
    """Show paginated search results."""
    if not update.effective_chat or not update.effective_user:
        raise Exception("Not chat or user in the update")

    recipe_repo = get_state()["recipe_repo"]
    filters = RecipeFilters(user_id=update.effective_user.id, tag_names=search_tags)
    recipes = await recipe_repo.list_filtered(filters)

    if not recipes:
        message = (
            f"No recipes found with tags: {', '.join(f'#{tag}' for tag in search_tags)}"
        )
        if edit_message and update.callback_query:
            await update.callback_query.edit_message_text(message)
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
            )
        return

    # Create paginated result
    paginated_result = PaginatedResult(
        recipes,
        page,
    )

    # Create paginated keyboard
    def item_callback_factory(recipe, current_page):
        return f"{SearchRecipesCallbackPattern.RESULT_PREFIX}{recipe.id}"

    search_info = f"Search results for: {', '.join(f'#{tag}' for tag in search_tags)}"

    reply_markup = create_paginated_keyboard(
        paginated_result,
        item_callback_factory,
        navigation_prefix=SearchRecipesCallbackPattern.RESULT_PAGE_PREFIX,
    )

    message_text = f"{search_info}\n\n{paginated_result.get_page_info_text()}"

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


async def handle_search_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle recipe selection from search results."""
    query = update.callback_query
    if not query or not query.data:
        return

    await query.answer()

    # Extract recipe ID from callback data
    if not query.data.startswith(SearchRecipesCallbackPattern.RESULT_PREFIX):
        return

    recipe_id = query.data[
        len(SearchRecipesCallbackPattern.RESULT_PREFIX) :
    ]  # Remove prefix

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

    if query.message:
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="What would you like to do next?",
            reply_markup=MAIN_KEYBOARD,
        )

    return True


async def handle_search_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle pagination navigation for search results."""
    query = update.callback_query
    if not query or not query.data:
        return

    await query.answer()

    # Parse pagination callback
    page = parse_pagination_callback(
        query.data, SearchRecipesCallbackPattern.RESULT_PAGE_PREFIX
    )
    if page is None:
        return

    # Get search tags from user data (we need to store them)
    if not context.user_data:
        await query.edit_message_text("Search session expired. Please search again.")
        return

    search_tags = context.user_data.get(SearchRecipesContextKey.SEARCH_TAGS, [])
    if not search_tags:
        await query.edit_message_text("Search session expired. Please search again.")
        return

    # Show the requested page
    await _show_search_results(
        update, context, search_tags, page=page, edit_message=True
    )

    return True
