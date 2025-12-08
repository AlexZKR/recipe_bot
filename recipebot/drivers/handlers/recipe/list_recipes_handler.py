from uuid import UUID

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from recipebot.drivers.handlers.main_keyboard import MAIN_KEYBOARD
from recipebot.drivers.state import get_state


async def list_recipes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or not update.effective_user:
        raise Exception("Not chat or user in the update")
    recipe_repo = get_state(context)["recipe_repo"]
    recipes = await recipe_repo.list_by_user(update.effective_user.id)

    if not recipes:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="You don't have any recipes yet. Use /add to create your first recipe!",
        )
        return

    # Create inline keyboard with recipe names
    keyboard = []
    for recipe in recipes:
        keyboard.append(
            [InlineKeyboardButton(recipe.title, callback_data=f"recipe_{recipe.id}")]
        )

    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Select a recipe to view:",
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
    callback_data = query.data
    if not callback_data or not callback_data.startswith("recipe_"):
        return

    recipe_id = callback_data[7:]  # Remove "recipe_" prefix

    # Get recipe details
    recipe_repo = get_state(context)["recipe_repo"]
    recipe = await recipe_repo.get(UUID(recipe_id))

    if not recipe:
        await query.edit_message_text("Recipe not found.")
        return

    # Format recipe details
    recipe_text = recipe.to_md()

    await query.edit_message_text(recipe_text, parse_mode="Markdown")

    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text="What would you like to do next?",
        reply_markup=MAIN_KEYBOARD,
    )


list_recipes_handler = CommandHandler("list", list_recipes)
recipe_selection_handler = CallbackQueryHandler(
    handle_recipe_selection, pattern=r"^recipe_"
)
