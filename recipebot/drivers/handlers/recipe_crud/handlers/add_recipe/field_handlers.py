from telegram import (
    Update,
)
from telegram.ext import ContextTypes, ConversationHandler

from recipebot.adapters.services.groq_parser.recipe_parser import GroqRecipeParser
from recipebot.domain.recipe.recipe import Recipe, RecipeCategory
from recipebot.drivers.handlers.main_keyboard import MAIN_KEYBOARD
from recipebot.drivers.handlers.recipe_crud.handlers.add_recipe.constants import (
    ADD_CATEGORY,
    ADD_CATEGORY_INVALID,
    ADD_INGREDIENTS,
    ADD_INGREDIENTS_PROCESSING,
    ADD_INGREDIENTS_SUCCESS,
    ADD_LINK,
    ADD_LINK_ADDED,
    ADD_LINK_INVALID,
    ADD_LINK_SKIP,
    ADD_STEPS,
    ADD_STEPS_PROCESSING,
    ADD_STEPS_SUCCESS,
    ADD_TAGS_DONE,
    CATEGORY,
    INGREDIENTS,
    LINK,
    STEPS,
    TAGS,
)
from recipebot.drivers.handlers.recipe_crud.handlers.add_recipe.layout import (
    show_tags_keyboard,
)
from recipebot.drivers.handlers.recipe_crud.handlers.add_recipe.utils import (
    add_tag_to_recipe,
    validate_source_link,
)
from recipebot.drivers.handlers.recipe_crud.shared.keyboards import (
    create_category_reply_keyboard,
)
from recipebot.drivers.state import get_state
from recipebot.metrics.recipes import RECIPES_CREATED, RecipeCreationSourceEnum


async def handle_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the title and asks for the ingredients."""
    if not update.message:
        raise Exception("Something went wrong")

    context.user_data["title"] = update.message.text  # type: ignore[index]
    await update.message.reply_text(ADD_INGREDIENTS)

    return INGREDIENTS


async def handle_ingredients(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the ingredients and asks for the steps."""
    if not update.message or not context.user_data:
        raise Exception("Something went wrong")

    await update.message.reply_text(ADD_INGREDIENTS_PROCESSING)

    recipe_parser = GroqRecipeParser(get_state()["groq_client"])
    ingredients = await recipe_parser.parse_ingredients(update.message.text or "")
    context.user_data["ingredients"] = [i.model_dump() for i in ingredients]
    await update.message.reply_text(ADD_INGREDIENTS_SUCCESS)

    await update.message.reply_text(ADD_STEPS)

    return STEPS


async def handle_steps(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the steps and asks for the category."""
    if not update.message or not context.user_data:
        raise Exception("Something went wrong")

    await update.message.reply_text(ADD_STEPS_PROCESSING)

    recipe_parser = GroqRecipeParser(get_state()["groq_client"])
    steps = await recipe_parser.parse_steps(update.message.text or "")
    context.user_data["steps"] = steps

    await update.message.reply_text(ADD_STEPS_SUCCESS)

    await update.message.reply_text(
        ADD_CATEGORY,
        reply_markup=create_category_reply_keyboard(),
    )

    return CATEGORY


async def handle_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the category and ends the conversation."""
    if not update.message or not context.user_data or not update.effective_user:
        raise Exception("Something went wrong")

    user_input = update.message.text

    # Validate that the input is a valid RecipeCategory
    try:
        RecipeCategory(user_input or "")
    except ValueError:
        # Invalid category, reprompt user
        await update.message.reply_text(
            ADD_CATEGORY_INVALID,
            reply_markup=create_category_reply_keyboard(),
        )
        return CATEGORY

    # Valid category, proceed to tags step
    context.user_data["category"] = user_input

    await update.message.reply_text(ADD_LINK)

    return LINK


async def handle_source_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the source link and asks for the tags."""
    if not update.message or not update.message.text or not context.user_data:
        raise Exception("Something went wrong")

    if not validate_source_link(update.message.text):
        await update.message.reply_text(
            ADD_LINK_INVALID,
        )
        return LINK

    context.user_data["source_link"] = update.message.text

    await update.message.reply_text(ADD_LINK_ADDED)

    # Show tags selection (message will be sent by show_tags_keyboard)
    await show_tags_keyboard(update, context)
    return TAGS


async def handle_skip_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skips the source link step and moves to tags selection."""
    if not update.message or not context.user_data:
        raise Exception("Something went wrong")

    # Don't set source_link, leaving it as None (skipped)
    await update.message.reply_text(ADD_LINK_SKIP)

    # Show tags selection (message will be sent by show_tags_keyboard)
    await show_tags_keyboard(update, context)
    return TAGS


async def handle_tags(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles tag selection and saving."""
    if not update.effective_user:
        raise Exception("Something went wrong")

    # Handle text input for new tags
    if update.message and update.message.text:
        # Handle new tag input
        tag_name = update.message.text.strip()
        if tag_name:
            await add_tag_to_recipe(context, tag_name)
        await show_tags_keyboard(update, context)
        return TAGS

    # If no valid input, show keyboard again
    await show_tags_keyboard(update, context)
    return TAGS


async def finalize_recipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save the recipe with tags to the database."""
    if not update.effective_user or not context.user_data:
        raise Exception("Something went wrong")

    # Get tags from context (already as tag names)
    tag_names = context.user_data.get("tags", [])

    link = context.user_data.get("source_link")
    # Check for TikTok source data
    if context.user_data.get("from_tiktok"):
        tiktok_data = context.user_data.get("tiktok_source", {})
        link = tiktok_data.get("link")

    # Save the recipe to the database
    recipe_repo = get_state()["recipe_repo"]
    recipe = Recipe(
        title=context.user_data["title"],
        ingredients=context.user_data["ingredients"],
        steps=context.user_data["steps"],
        category=RecipeCategory(context.user_data["category"]),
        user_id=update.effective_user.id,
        tags=tag_names,
        desc=context.user_data.get("desc"),
        estimated_time=context.user_data.get("estimated_time"),
        link=link,
    )
    await recipe_repo.add(recipe)

    # instrumentation
    if context.user_data.get("from_tiktok"):
        RECIPES_CREATED.labels(source=RecipeCreationSourceEnum.TIKTOK_MANUAL).inc()
    else:
        RECIPES_CREATED.labels(source=RecipeCreationSourceEnum.MANUAL).inc()

    # Display the newly added recipe
    if update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="✅ Recipe added successfully!\n\n" + recipe.to_md(),
            # Remove parse_mode to avoid markdown parsing issues
        )

    if update.callback_query:
        await update.callback_query.edit_message_text(ADD_TAGS_DONE, reply_markup=None)

    if update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="What would you like to do next?",
            reply_markup=MAIN_KEYBOARD,
        )

    context.user_data.clear()
    return ConversationHandler.END
