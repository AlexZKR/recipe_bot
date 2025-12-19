import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from recipebot.adapters.repositories.sql.recipe.recipe_filters import RecipeFilters
from recipebot.drivers.handlers.auth.decorators import only_registered
from recipebot.drivers.handlers.main_keyboard import MAIN_KEYBOARD
from recipebot.drivers.handlers.recipe_crud.handlers.list_recipes.handler import (
    _show_recipe_list,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.category_search.category_display import (
    show_category_selection,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.handler_context import (
    SearchRecipesCallbackPattern,
    SearchRecipesContextKey,
    SearchRecipesMode,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.layout import (
    create_search_mode_keyboard,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.messages import (
    SEARCH_INIT_MESSAGE,
    SEARCH_MODE_SELECTION_MESSAGE,
    get_current_filters_message,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.tag_search.tag_handlers import (
    show_tag_selection,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.utils import (
    get_selected_filters,
)
from recipebot.drivers.handlers.recipe_crud.shared import (
    create_filter_description,
)
from recipebot.drivers.state import get_state

logger = logging.getLogger(__name__)


@only_registered
async def search_recipes_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start recipe search by showing available tags."""
    if not update.effective_chat or not update.effective_user:
        raise Exception("Not chat or user in the update")

    if context.user_data is None:
        context.user_data = {
            SearchRecipesContextKey.SELECTED_TAGS: [],
            SearchRecipesContextKey.SELECTED_CATEGORIES: [],
        }

    logger.info("User initiated recipe search")

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=SEARCH_INIT_MESSAGE.format(
            current_filters=get_current_filters_message(context)
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=create_search_mode_keyboard(),
    )


async def handle_search_mode_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Handle search mode selection."""
    query = update.callback_query

    # Handle callback query (when called from button press)
    if query and query.data:
        # Handle search execution
        if query.data == SearchRecipesCallbackPattern.SEARCH_PREFIX:
            await query.answer()
            logger.debug("User pressed search button")
            await handle_search_execution(update, context)
            return True

        # Handle mode selection
        elif query.data.startswith(SearchRecipesCallbackPattern.MODE_PREFIX):
            await query.answer()
            logger.debug(f"Mode selection callback received: '{query.data}'")
            mode = query.data[len(SearchRecipesCallbackPattern.MODE_PREFIX) :]
            logger.debug(f"Extracted mode: '{mode}' (length: {len(mode)})")

            # Handle back button (empty mode = return to mode selection)
            if not mode:
                logger.debug("User pressed back to mode selection")
                await _show_mode_selection_screen(update, context)
                return True

            match mode:
                case SearchRecipesMode.CATEGORY:
                    logger.debug("User selected category search mode")
                    await show_category_selection(update, context)
                    return True
                case SearchRecipesMode.TAG:
                    logger.debug("User selected tag search mode")
                    await show_tag_selection(update, context)
                    return True
                case _:
                    logger.warning(f"Unknown search mode selected: {mode or 'empty'}")
                    return True
    else:
        # Handle direct call (when called from other handlers like tag selection)
        logger.debug("Returning to mode selection")
        await _show_mode_selection_screen(update, context)


async def handle_search_execution(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute search with current filters and show results."""
    if not update.effective_chat or not update.effective_user:
        raise Exception("Not chat or user in the update")

    # Get selected filters from user_data
    selected_tags, selected_categories = get_selected_filters(context)

    # Create filters
    filters = RecipeFilters(
        user_id=update.effective_user.id,
        tag_names=selected_tags,
        category_names=selected_categories,
    )

    # Check if there are any recipes with these filters
    recipe_repo = get_state()["recipe_repo"]
    recipes = await recipe_repo.list_filtered(filters)

    if not recipes:
        # No recipes found - show message and return to mode selection
        filter_desc = create_filter_description(filters)
        error_message = f"No recipes found{filter_desc}. Try adjusting your filters or use /add to create a new recipe!"

        # Return to mode selection screen with error message
        if update.callback_query:
            await update.callback_query.answer()
        await _show_mode_selection_screen(update, context, error_message=error_message)
        return

    # Recipes found - show them using list_recipes logic
    if update.callback_query:
        await update.callback_query.answer()

    # Clear the filters since search was successful
    if context.user_data:
        context.user_data.pop(SearchRecipesContextKey.SELECTED_TAGS, None)
        context.user_data.pop(SearchRecipesContextKey.SELECTED_CATEGORIES, None)

    await _show_recipe_list(
        update,
        context,
        page=1,
        edit_message=True,  # Edit the search message instead of sending new one
        filters=filters,
    )

    # Send message about using main keyboard for other actions
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Use the keyboard below to perform other actions:",
        reply_markup=MAIN_KEYBOARD,
    )


async def _show_mode_selection_screen(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    edit_message: bool = True,
    error_message: str | None = None,
):
    """Show the mode selection screen with current filter status."""
    if not update.effective_chat or not update.effective_user:
        raise Exception("Not chat or user in the update")

    base_text = SEARCH_MODE_SELECTION_MESSAGE.format(
        current_filters=get_current_filters_message(context)
    )

    if error_message:
        text = f"{error_message}\n\n{base_text}"
    else:
        text = base_text
    reply_markup = create_search_mode_keyboard()

    if edit_message and update.callback_query:
        await update.callback_query.edit_message_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup,
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup,
        )
