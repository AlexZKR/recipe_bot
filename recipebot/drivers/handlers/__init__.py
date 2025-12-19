from telegram.ext import MessageHandler, filters
from telegram.ext._application import Application

from recipebot.drivers.handlers.auth import registered_handler, start_handler
from recipebot.drivers.handlers.auth.decorators import only_registered
from recipebot.drivers.handlers.main_keyboard import MAIN_KEYBOARD
from recipebot.drivers.handlers.recipe_crud.handlers.add_recipe import (
    add_recipe_handler,
)
from recipebot.drivers.handlers.recipe_crud.handlers.delete_recipe import (
    delete_confirmation_handler,
    delete_pagination_handler,
    delete_recipe_handler,
    delete_recipe_selection_handler,
)
from recipebot.drivers.handlers.recipe_crud.handlers.edit_recipe import (
    edit_category_selection_handler,
    edit_field_conversation,
    edit_field_selection_handler,
    edit_pagination_handler,
    edit_recipe_selection_handler,
    update_recipe_handler,
)
from recipebot.drivers.handlers.recipe_crud.handlers.from_tiktok import (
    from_tiktok_handler,
)
from recipebot.drivers.handlers.recipe_crud.handlers.list_recipes import (
    list_pagination_handler,
    list_recipes_handler,
    recipe_selection_handler,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes import (
    search_mode_selection_handler,
    search_pagination_handler,
    search_recipes_handler,
    search_result_handler,
    search_tag_pagination_handler,
    search_tag_selection_handler,
)
from recipebot.drivers.handlers.recipe_crud.shared_tag_callbacks import (
    global_tag_callback_handler,
)
from recipebot.drivers.middleware import logging_middleware_handler


@only_registered
async def show_main_keyboard(update, context):
    """Show the main keyboard with available commands."""
    if not update.effective_chat:
        raise Exception("No chat in the update")

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="What would you like to do?",
        reply_markup=MAIN_KEYBOARD,
    )


# Fallback handler for unrecognized messages
fallback_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, show_main_keyboard)


def add_handlers(app: Application) -> None:
    # Add middleware first (runs for all updates)
    app.add_handler(logging_middleware_handler, group=-1)

    # Add all other handlers
    app.add_handler(start_handler)
    app.add_handler(registered_handler)
    app.add_handler(add_recipe_handler)
    app.add_handler(from_tiktok_handler)
    app.add_handler(list_recipes_handler)
    app.add_handler(recipe_selection_handler)
    app.add_handler(edit_recipe_selection_handler)
    app.add_handler(edit_field_selection_handler)
    app.add_handler(edit_pagination_handler)
    app.add_handler(delete_recipe_selection_handler)
    app.add_handler(delete_confirmation_handler)
    app.add_handler(delete_pagination_handler)
    app.add_handler(search_mode_selection_handler)
    app.add_handler(search_result_handler)
    app.add_handler(search_tag_pagination_handler)
    app.add_handler(search_tag_selection_handler)
    app.add_handler(global_tag_callback_handler)
    app.add_handler(list_pagination_handler)
    app.add_handler(search_recipes_handler)
    app.add_handler(search_pagination_handler)
    app.add_handler(update_recipe_handler)
    app.add_handler(edit_field_conversation)
    app.add_handler(edit_category_selection_handler)
    app.add_handler(delete_recipe_handler)
    app.add_handler(fallback_handler)
