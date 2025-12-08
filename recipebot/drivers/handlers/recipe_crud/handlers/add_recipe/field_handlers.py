from telegram import ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler

from recipebot.domain.recipe.recipe import Recipe, RecipeCategory
from recipebot.drivers.handlers.main_keyboard import MAIN_KEYBOARD
from recipebot.drivers.handlers.recipe_crud.handlers.add_recipe.constants import (
    ADD_CANCEL,
    ADD_CATEGORY,
    ADD_CATEGORY_INVALID,
    ADD_DONE,
    ADD_INGREDIENTS,
    ADD_STEPS,
    CATEGORY,
    INGREDIENTS,
    STEPS,
)
from recipebot.drivers.handlers.recipe_crud.handlers.add_recipe.layout import (
    create_category_keyboard,
)
from recipebot.drivers.state import get_state


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

    context.user_data["ingredients"] = update.message.text
    await update.message.reply_text(ADD_STEPS)

    return STEPS


async def handle_steps(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the steps and asks for the category."""
    if not update.message or not context.user_data:
        raise Exception("Something went wrong")

    context.user_data["steps"] = update.message.text
    await update.message.reply_text(
        ADD_CATEGORY,
        reply_markup=create_category_keyboard(),
    )

    return CATEGORY


async def handle_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the category and ends the conversation."""
    if not update.message or not context.user_data or not update.effective_user:
        raise Exception("Something went wrong")

    user_input = update.message.text

    # Validate that the input is a valid RecipeCategory
    try:
        recipe_category = RecipeCategory(user_input or "")
    except ValueError:
        # Invalid category, reprompt user
        await update.message.reply_text(
            ADD_CATEGORY_INVALID,
            reply_markup=create_category_keyboard(),
        )
        return CATEGORY

    # Valid category, proceed with saving
    context.user_data["category"] = user_input
    await update.message.reply_text(ADD_DONE, reply_markup=ReplyKeyboardRemove())

    # Save the recipe to the database
    recipe_repo = get_state(context)["recipe_repo"]
    recipe = Recipe(
        title=context.user_data["title"],
        ingredients=context.user_data["ingredients"],
        steps=context.user_data["steps"],
        category=recipe_category,
        user_id=update.effective_user.id,
    )
    await recipe_repo.add(recipe)

    await update.message.reply_text(
        "Recipe saved! What would you like to do next?",
        reply_markup=MAIN_KEYBOARD,
    )

    context.user_data.clear()
    return ConversationHandler.END


async def handle_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    if not context.user_data:
        raise Exception("Something went wrong")
    if not update.message:
        raise Exception("No message in the update")

    await update.message.reply_text(ADD_CANCEL, reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END
