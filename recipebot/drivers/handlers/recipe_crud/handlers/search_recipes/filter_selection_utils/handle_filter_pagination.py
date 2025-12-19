"""Generic filter pagination callback handlers."""

from collections.abc import Awaitable, Callable

from telegram import Update
from telegram.ext import ContextTypes

from recipebot.drivers.handlers.recipe_crud.shared import parse_pagination_callback


async def handle_generic_filter_pagination(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    page_prefix: str,
    show_function: Callable[[Update, ContextTypes.DEFAULT_TYPE, int], Awaitable[None]],
):
    """Generic handler for filter pagination callbacks.

    Args:
        update: Telegram update
        context: Telegram context
        page_prefix: The pagination callback prefix for this filter type
        show_function: Function to call to show the page
    """
    query = update.callback_query
    if not query or not query.data:
        return

    await query.answer()

    page = parse_pagination_callback(query.data, page_prefix)
    if page is None:
        return

    await show_function(update, context, page)

    return True
