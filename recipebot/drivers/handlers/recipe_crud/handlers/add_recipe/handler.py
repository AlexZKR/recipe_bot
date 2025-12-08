from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from recipebot.drivers.handlers.auth.decorators import only_registered
from recipebot.drivers.handlers.recipe_crud.handlers.add_recipe.constants import (
    ADD_START,
    ADD_TITLE,
    CATEGORY,
    INGREDIENTS,
    STEPS,
    TITLE,
)
from recipebot.drivers.handlers.recipe_crud.handlers.add_recipe.field_handlers import (
    handle_cancel,
    handle_category,
    handle_ingredients,
    handle_steps,
    handle_title,
)


@only_registered
async def add_recipe_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks for a title."""
    if not update.effective_chat:
        raise Exception("No chat in the update")

    await context.bot.send_message(chat_id=update.effective_chat.id, text=ADD_START)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=ADD_TITLE)

    return TITLE


# Conversation handler for adding recipes
add_recipe_handler = ConversationHandler(
    entry_points=[CommandHandler("add", add_recipe_start)],
    states={
        TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_title)],
        INGREDIENTS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ingredients)
        ],
        STEPS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_steps)],
        CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_category)],
    },
    fallbacks=[CommandHandler("cancel", handle_cancel)],
    persistent=True,
    name="add_recipe_conversation",
)
