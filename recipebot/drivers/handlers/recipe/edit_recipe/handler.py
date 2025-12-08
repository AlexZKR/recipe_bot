from uuid import UUID
from warnings import filterwarnings

from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from telegram.warnings import PTBUserWarning

from recipebot.drivers.handlers.main_keyboard import MAIN_KEYBOARD
from recipebot.drivers.handlers.recipe.edit_recipe.constants import (
    EDIT_RECIPE_PREFIX,
    EDITING_CATEGORY,
    EDITING_DESCRIPTION,
    EDITING_INGREDIENTS,
    EDITING_LINK,
    EDITING_NOTES,
    EDITING_SERVINGS,
    EDITING_STEPS,
    EDITING_TIME,
    EDITING_TITLE,
)
from recipebot.drivers.handlers.recipe.edit_recipe.field_handlers import (
    save_category,
    save_description,
    save_ingredients,
    save_link,
    save_notes,
    save_servings,
    save_steps,
    save_time,
    save_title,
)
from recipebot.drivers.handlers.recipe.edit_recipe.handler_context import (
    EditRecipeContextKey,
)
from recipebot.drivers.handlers.recipe.edit_recipe.layout import (
    create_field_edit_prompt,
    create_field_selection_keyboard,
)
from recipebot.drivers.handlers.recipe.edit_recipe.utils import (
    parse_edit_field_callback,
    parse_edit_recipe_callback,
    start_field_editing,
)
from recipebot.drivers.handlers.recipe.list_recipes_handler import (
    create_recipe_selection_keyboard,
)
from recipebot.drivers.state import get_state
from recipebot.ports.repositories.exceptions import RecipeNotFound

filterwarnings(
    action="ignore", message=r".*CallbackQueryHandler.*", category=PTBUserWarning
)


async def update_recipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the recipe update process by showing recipe selection."""
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

    # Create inline keyboard with recipe names for editing
    reply_markup = create_recipe_selection_keyboard(recipes, EDIT_RECIPE_PREFIX)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Select a recipe to edit:",
        reply_markup=reply_markup,
    )

    # Also show the main keyboard below
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Or use the keyboard below:",
        reply_markup=MAIN_KEYBOARD,
    )


async def handle_recipe_selection_for_edit(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Handle recipe selection for editing - show field selection options."""
    query = update.callback_query
    if not query or not query.message or not query.message.chat:
        return

    await query.answer()

    # Extract recipe ID from callback data
    recipe_id = parse_edit_recipe_callback(query.data)
    if not recipe_id:
        return

    # Get recipe details to show current values
    recipe_repo = get_state(context)["recipe_repo"]
    try:
        recipe = await recipe_repo.get(UUID(recipe_id))
    except RecipeNotFound:
        await query.edit_message_text("Recipe not found.")
        return

    # Store recipe in user context to avoid re-querying
    # Note: editing_field will be set when field is selected
    if context.user_data is None:
        context.user_data = {}
    context.user_data[EditRecipeContextKey.EDITING_RECIPE] = recipe

    # Create field selection keyboard
    reply_markup = create_field_selection_keyboard(recipe)

    await query.edit_message_text(
        f"Editing recipe: **{recipe.title}**\n\nWhat would you like to change?",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def handle_field_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle field selection and start editing conversation."""
    query = update.callback_query
    if not query or not query.message or not query.message.chat:
        return

    await query.answer()

    callback_data = query.data
    if callback_data is None:
        return

    parsed = parse_edit_field_callback(callback_data)
    if not parsed:
        return

    recipe_id, field_name = parsed

    # Get recipe from user context (already fetched in previous step)
    if context.user_data is None:
        await query.edit_message_text("Session expired. Please start over.")
        return

    recipe = context.user_data.get(EditRecipeContextKey.EDITING_RECIPE)
    if not recipe:
        await query.edit_message_text("Recipe not found in session. Please start over.")
        return

    # Show current value and prompt for new value
    prompt = create_field_edit_prompt(recipe, field_name)

    # Remove keyboard and show input prompt
    await query.edit_message_text(prompt, parse_mode="Markdown", reply_markup=None)

    # Start the editing conversation and return the appropriate state
    return start_field_editing(context, recipe_id, field_name)


async def cancel_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the editing process."""
    if not update.message:
        return ConversationHandler.END

    await update.message.reply_text("Edit cancelled.", reply_markup=MAIN_KEYBOARD)
    if context.user_data:
        context.user_data.clear()
    return ConversationHandler.END


# Handlers
update_recipe_handler = CommandHandler("edit_recipe", update_recipe)
edit_recipe_selection_handler = CallbackQueryHandler(
    handle_recipe_selection_for_edit,
    pattern=r"^edit_recipe_",  # Matches EDIT_RECIPE_PREFIX
)
edit_field_selection_handler = CallbackQueryHandler(
    handle_field_selection, pattern=r"^edit_field_"
)

# Conversation handler for field editing
edit_field_conversation = ConversationHandler(
    entry_points=[edit_field_selection_handler],
    states={
        EDITING_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_title)],
        EDITING_INGREDIENTS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, save_ingredients)
        ],
        EDITING_STEPS: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_steps)],
        EDITING_CATEGORY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, save_category)
        ],
        EDITING_SERVINGS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, save_servings)
        ],
        EDITING_DESCRIPTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, save_description)
        ],
        EDITING_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_time)],
        EDITING_NOTES: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_notes)],
        EDITING_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_link)],
    },
    fallbacks=[CommandHandler("cancel", cancel_edit)],
    persistent=True,
    per_message=False,
    name="edit_recipe_conversation",
)
