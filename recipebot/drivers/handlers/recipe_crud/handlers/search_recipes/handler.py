import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

# Logging context is now handled automatically by middleware
from recipebot.drivers.handlers.auth.decorators import only_registered
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.category_search.search_category_utils import (
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
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.tag_search.tag_display import (
    show_tag_selection,
)

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
    if (
        query
        and query.data
        and query.data.startswith(SearchRecipesCallbackPattern.MODE_PREFIX)
    ):
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
                await show_tag_selection(update, context, edit_message=True)
                return True
            case _:
                logger.warning(f"Unknown search mode selected: {mode or 'empty'}")
                return True
    else:
        # Handle direct call (when called from other handlers like tag selection)
        logger.debug("Returning to mode selection")
        await _show_mode_selection_screen(update, context)


async def _show_mode_selection_screen(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Show the mode selection screen with current filter status."""
    if not update.effective_chat or not update.effective_user:
        raise Exception("Not chat or user in the update")

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=SEARCH_MODE_SELECTION_MESSAGE.format(
            current_filters=get_current_filters_message(context)
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=create_search_mode_keyboard(),
    )
