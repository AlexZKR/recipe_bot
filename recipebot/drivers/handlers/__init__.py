from telegram.ext import MessageHandler, filters
from telegram.ext._application import Application

from recipebot.drivers.handlers.auth import registered_handler, start_handler
from recipebot.drivers.handlers.auth.decorators import only_registered
from recipebot.drivers.handlers.main_keyboard import MAIN_KEYBOARD
from recipebot.drivers.handlers.recipe.add_recipe_handler import add_recipe_handler
from recipebot.drivers.handlers.recipe.edit_recipe import (
    edit_field_conversation,
    edit_recipe_selection_handler,
    update_recipe_handler,
)
from recipebot.drivers.handlers.recipe.list_recipes_handler import (
    list_recipes_handler,
    recipe_selection_handler,
)


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
    app.add_handler(start_handler)
    app.add_handler(registered_handler)
    app.add_handler(add_recipe_handler)
    app.add_handler(list_recipes_handler)
    app.add_handler(recipe_selection_handler)
    app.add_handler(update_recipe_handler)
    app.add_handler(edit_recipe_selection_handler)
    app.add_handler(edit_field_conversation)
    app.add_handler(fallback_handler)
