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

from recipebot.domain.recipe.recipe import RecipeCategory
from recipebot.drivers.handlers.basic_fallback import basic_fallback_handler
from recipebot.drivers.handlers.main_keyboard import MAIN_KEYBOARD
from recipebot.drivers.handlers.recipe_crud.handlers.edit_recipe.constants import (
    EDIT_CATEGORY_MIN_PARTS,
    EDITING_DESCRIPTION,
    EDITING_INGREDIENTS,
    EDITING_LINK,
    EDITING_NOTES,
    EDITING_SERVINGS,
    EDITING_STEPS,
    EDITING_TIME,
    EDITING_TITLE,
)
from recipebot.drivers.handlers.recipe_crud.handlers.edit_recipe.field_handlers import (
    save_description,
    save_ingredients,
    save_link,
    save_notes,
    save_servings,
    save_steps,
    save_time,
    save_title,
)
from recipebot.drivers.handlers.recipe_crud.handlers.edit_recipe.handler_context import (
    EditRecipeContextKey,
)
from recipebot.drivers.handlers.recipe_crud.handlers.edit_recipe.layout import (
    create_category_selection_keyboard,
    create_field_selection_keyboard,
)
from recipebot.drivers.handlers.recipe_crud.handlers.edit_recipe.utils import (
    create_field_edit_prompt,
    parse_edit_field_callback,
    parse_edit_recipe_callback,
    start_field_editing,
)
from recipebot.drivers.handlers.recipe_crud.shared import (
    PaginatedResult,
    create_paginated_keyboard,
    parse_pagination_callback,
)
from recipebot.drivers.state import get_state
from recipebot.ports.repositories.exceptions import RecipeNotFound

filterwarnings(
    action="ignore", message=r".*CallbackQueryHandler.*", category=PTBUserWarning
)


async def update_recipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the recipe update process by showing paginated recipe selection."""
    await _show_edit_recipe_list(update, context, page=1)


async def _show_edit_recipe_list(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    page: int = 1,
    edit_message: bool = False,
):
    """Show paginated recipe list for editing."""
    if not update.effective_chat or not update.effective_user:
        raise Exception("Not chat or user in the update")

    recipe_repo = get_state()["recipe_repo"]
    recipes = await recipe_repo.list_by_user(update.effective_user.id)

    if not recipes:
        message = (
            "You don't have any recipes yet. Use /add to create your first recipe!"
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
    paginated_result = PaginatedResult(recipes, page, callback_prefix="edit_recipe_")

    # Create paginated keyboard
    def item_callback_factory(recipe, current_page):
        return f"edit_recipe_{recipe.id}"

    reply_markup = create_paginated_keyboard(
        paginated_result, item_callback_factory, navigation_prefix="edit_page"
    )

    message_text = (
        f"Select a recipe to edit:\n\n{paginated_result.get_page_info_text()}"
    )

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


async def handle_edit_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle pagination navigation for edit recipe list."""
    query = update.callback_query
    if not query or not query.data:
        return

    await query.answer()

    # Parse pagination callback
    page = parse_pagination_callback(query.data, "edit_page")
    if page is None:
        return

    # Show the requested page
    await _show_edit_recipe_list(update, context, page=page, edit_message=True)


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
    recipe_repo = get_state()["recipe_repo"]
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
    )


async def handle_field_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):  # noqa: PLR0911
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
    print(
        f"DEBUG: handle_field_selection parsed: recipe_id='{recipe_id}', field_name='{field_name}'"
    )  # Debug

    # Get recipe from user context (already fetched in previous step)
    if context.user_data is None:
        await query.edit_message_text("Session expired. Please start over.")
        return

    recipe = context.user_data.get(EditRecipeContextKey.EDITING_RECIPE)
    if not recipe:
        await query.edit_message_text("Recipe not found in session. Please start over.")
        return

    # Special handling for category field - show category selection keyboard
    if field_name == "category":
        reply_markup = create_category_selection_keyboard(recipe_id)
        await query.edit_message_text(
            f"Editing recipe: **{recipe.title}**\n\nSelect the new category:",
            reply_markup=reply_markup,
        )
        # Don't start conversation for category - handle via callback
        return

    # For other fields, show text prompt and start conversation
    prompt = create_field_edit_prompt(recipe, field_name)

    # Remove keyboard and show input prompt
    await query.edit_message_text(prompt, parse_mode="Markdown", reply_markup=None)

    # Start the editing conversation and return the appropriate state
    result_state = start_field_editing(context, recipe_id, field_name)
    print(f"DEBUG: handle_field_selection returning state: {result_state}")  # Debug
    return result_state


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
edit_pagination_handler = CallbackQueryHandler(
    handle_edit_pagination, pattern=r"^edit_page_"
)


async def handle_category_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle category selection for editing."""
    query = update.callback_query
    if not query or not query.message or not query.message.chat:
        return

    await query.answer()

    # Parse callback data: edit_category_{recipe_id}_{category_value}
    callback_data = query.data
    if not callback_data or not callback_data.startswith("edit_category_"):
        return

    # Remove prefix and split the remaining parts
    remaining = callback_data[len("edit_category_") :]
    parts = remaining.split("_", 1)  # Split only on first underscore to handle UUIDs
    if len(parts) != EDIT_CATEGORY_MIN_PARTS:
        return

    recipe_id = parts[0]
    category_value = parts[1]

    # Validate category
    try:
        category = RecipeCategory(category_value)
    except ValueError:
        await query.edit_message_text("Invalid category selected.")
        return

    # Get recipe and update category
    recipe_repo = get_state()["recipe_repo"]
    try:
        recipe = await recipe_repo.get(UUID(recipe_id))
    except RecipeNotFound:
        await query.edit_message_text("Recipe not found.")
        return

    # Update the category
    recipe.category = category

    # Save back to database
    try:
        await recipe_repo.update(recipe)
    except ValueError as e:
        await query.edit_message_text(f"Error updating recipe: {str(e)}")
        return

    await query.edit_message_text(
        f"✅ Category updated to **{category.value}** successfully!",
        reply_markup=None,
    )

    # Send the main keyboard
    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text="What would you like to do next?",
        reply_markup=MAIN_KEYBOARD,
    )


edit_category_selection_handler = CallbackQueryHandler(
    handle_category_selection, pattern=r"^edit_category_"
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
    fallbacks=[CommandHandler("cancel", cancel_edit), basic_fallback_handler],  # type: ignore[list-item]
    persistent=True,
    per_message=False,
    conversation_timeout=300,  # 5 minutes timeout
    name="edit_recipe_conversation",
)
