from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from recipebot.domain.recipe.recipe import Recipe, RecipeCategory
from recipebot.drivers.handlers.auth.decorators import only_registered
from recipebot.drivers.handlers.main_keyboard import MAIN_KEYBOARD
from recipebot.drivers.state import get_state

ADD_START = "Let's add a recipe. I will ask for the required info. You can cancel at any time by typing /cancel."
ADD_TITLE = "Provide a title for your recipe"
ADD_INGREDIENTS = "Great! Now provide the ingredients."
ADD_STEPS = "Awesome. Now, the steps to prepare it."
ADD_CATEGORY = (
    "What category does this recipe belong to (use keyboard for range of options)?"
)
ADD_CATEGORY_INVALID = (
    "Please select a valid category from the keyboard options provided."
)
ADD_DONE = "All done! Your recipe has been saved."
ADD_CANCEL = "Okay, I've cancelled the process. Your recipe has not been saved."

TITLE, INGREDIENTS, STEPS, CATEGORY = range(4)


@only_registered
async def add_recipe_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks for a title."""
    if not update.effective_chat:
        raise Exception("No chat in the update")

    await context.bot.send_message(chat_id=update.effective_chat.id, text=ADD_START)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=ADD_TITLE)

    return TITLE


async def title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the title and asks for the ingredients."""
    if not update.message:
        raise Exception("Something went wrong")

    context.user_data["title"] = update.message.text  # type: ignore[index]
    await update.message.reply_text(ADD_INGREDIENTS)

    return INGREDIENTS


async def ingredients(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the ingredients and asks for the steps."""
    if not update.message or not context.user_data:
        raise Exception("Something went wrong")

    context.user_data["ingredients"] = update.message.text
    await update.message.reply_text(ADD_STEPS)

    return STEPS


async def steps(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the steps and asks for the category."""
    if not update.message or not context.user_data:
        raise Exception("Something went wrong")

    context.user_data["steps"] = update.message.text
    reply_keyboard = [[category.value for category in RecipeCategory]]
    await update.message.reply_text(
        ADD_CATEGORY,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            selective=True,
            one_time_keyboard=True,
            input_field_placeholder="Recipe category",
        ),
    )

    return CATEGORY


async def category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the category and ends the conversation."""
    if not update.message or not context.user_data or not update.effective_user:
        raise Exception("Something went wrong")

    user_input = update.message.text

    # Validate that the input is a valid RecipeCategory
    try:
        recipe_category = RecipeCategory(user_input or "")
    except ValueError:
        # Invalid category, reprompt user
        reply_keyboard = [[category.value for category in RecipeCategory]]
        await update.message.reply_text(
            ADD_CATEGORY_INVALID,
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,
                selective=True,
                one_time_keyboard=True,
                input_field_placeholder="Recipe category",
            ),
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


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    if not context.user_data:
        raise Exception("Something went wrong")
    if not update.message:
        raise Exception("No message in the update")

    await update.message.reply_text(ADD_CANCEL, reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END


add_recipe_handler = ConversationHandler(
    entry_points=[CommandHandler("add", add_recipe_start)],
    states={
        TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, title)],
        INGREDIENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ingredients)],
        STEPS: [MessageHandler(filters.TEXT & ~filters.COMMAND, steps)],
        CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, category)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    persistent=True,
    name="add_recipe_conversation",
)
