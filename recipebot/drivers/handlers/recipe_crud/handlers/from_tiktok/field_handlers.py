
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes, ConversationHandler

from recipebot.adapters.services.groq_parser.recipe_parser import (
    GroqRecipeParser,
)
from recipebot.adapters.services.tt_resolver import HttpxTTResolver, TTResolverABC
from recipebot.domain.recipe.recipe import Recipe, RecipeCategory, RecipeDTO
from recipebot.drivers.handlers.basic_fallback import MAIN_KEYBOARD
from recipebot.drivers.handlers.recipe_crud.handlers.add_recipe.field_handlers import (
    add_tag_to_recipe,
    show_tags_keyboard,
)
from recipebot.drivers.handlers.recipe_crud.handlers.from_tiktok.constants import (
    CATEGORY,
    MANUAL_ENTRY,
    TAGS,
    TIKTOK_CANCEL,
    TIKTOK_CATEGORY,
    TIKTOK_MANUAL_ENTRY_PROMPT,
    TIKTOK_PROCESSING,
    TIKTOK_PROCESSING_ERROR,
    TIKTOK_PROCESSING_FAILED,
    TIKTOK_PROCESSING_SUCCESS,
    TIKTOK_SAVE_SUCCESS,
    URL,
)
from recipebot.drivers.handlers.recipe_crud.handlers.from_tiktok.handler_context import (
    TikTokRecipeContextKey,
)
from recipebot.drivers.handlers.recipe_crud.shared.keyboards import (
    create_category_reply_keyboard,
)
from recipebot.drivers.state import get_state
from recipebot.infra.transport.httpx_transport import init_transport
from recipebot.metrics.recipes import RECIPES_CREATED, RecipeCreationSourceEnum
from recipebot.ports.repositories.recipe_repository import RecipeRepositoryABC
from recipebot.ports.services.tt_resolver.exceptions import (
    InvalidTikTokURL,
    TikTokNotAccessible,
)
from recipebot.tasks.recipe_from_tt.recipe_from_tt import RecipeFromTTTask


async def handle_tiktok_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle TikTok URL input and process it."""
    if not update.message or not update.message.text:
        await update.message.reply_text(
            "Please send a valid TikTok URL."
        ) if update.message else None
        return URL

    if not update.effective_user:
        await update.message.reply_text("You must be registered to use this feature.")
        return URL

    user_input = update.message.text.strip()

    # Send processing message
    await update.message.reply_text(TIKTOK_PROCESSING)

    try:
        # Get dependencies from bot data
        async with init_transport() as transport:
            tt_resolver: TTResolverABC = HttpxTTResolver(transport)
            recipe_parser = GroqRecipeParser(get_state()["groq_client"])
            task = RecipeFromTTTask(
                tt_resolver=tt_resolver,
                recipe_parser=recipe_parser,
            )
            recipe_dto: RecipeDTO = await task.run(user_input)

        if context.user_data is None:
            context.user_data = {}
        context.user_data[TikTokRecipeContextKey.PARSED_RECIPE] = (
            recipe_dto.model_dump()
        )

        await update.message.reply_text("📱 Here's your recipe from TikTok:\n")
        await update.message.reply_text(recipe_dto.to_md())

        if len(recipe_dto.ingredients) == 0:
            return await handle_manual_entry_choice(update, context)

        await update.message.reply_text(TIKTOK_PROCESSING_SUCCESS)

        # Display the parsed recipe

        # Explain next steps for enhancing the recipe
        await update.message.reply_text(
            "🔧 **Let's enhance your recipe for better search and organization!**\n"
            "Please add a category and tags to make it easier to find later."
        )

        await update.message.reply_text(
            TIKTOK_CATEGORY,
            reply_markup=create_category_reply_keyboard(),
        )

        return CATEGORY

    except (InvalidTikTokURL, TikTokNotAccessible) as e:
        await update.message.reply_text(
            f"{TIKTOK_PROCESSING_ERROR}\n\nError: {str(e)}\n You can submit a valid URL or /cancel"
        )
        return URL
    except Exception as e:
        await update.message.reply_text(
            f"{TIKTOK_PROCESSING_ERROR}\n\nUnexpected error: {str(e)}\nYou can /cancel and try again"
        )
        return URL


async def handle_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the category and moves to tags selection."""
    if not update.message or not context.user_data:
        raise Exception("Something went wrong")

    user_input = update.message.text

    # Validate that the input is a valid RecipeCategory
    try:
        RecipeCategory(user_input or "")
    except ValueError:
        await update.message.reply_text(
            "Please select a valid category from the keyboard options provided.",
            reply_markup=create_category_reply_keyboard(),
        )
        return CATEGORY

    # Valid category, proceed to tags step
    context.user_data[TikTokRecipeContextKey.CATEGORY] = user_input

    # Show tags selection
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
            add_tag_to_recipe(context, tag_name)
        await show_tags_keyboard(update, context)
        return TAGS

    # If no valid input, show keyboard again
    await show_tags_keyboard(update, context)
    return TAGS


async def finalize_tiktok_recipe(  # noqa: PLR0912
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Finalize and save the TikTok recipe."""
    if not update.effective_user or not context.user_data:
        raise Exception("Something went wrong")

    # Determine how to send messages based on update type
    use_callback = update.callback_query is not None

    try:
        # Get the parsed recipe data
        parsed_recipe_data = context.user_data.get(TikTokRecipeContextKey.PARSED_RECIPE)
        if not parsed_recipe_data:
            if use_callback and update.callback_query:
                await update.callback_query.edit_message_text(
                    "Error: No recipe data found. Please start over."
                )
            elif not use_callback and update.message:
                await update.message.reply_text(
                    "Error: No recipe data found. Please start over."
                )
            # Clear user data to allow new conversations
            if context.user_data:
                context.user_data.clear()
            return ConversationHandler.END

        # Get user selections
        category = context.user_data.get(TikTokRecipeContextKey.CATEGORY)
        if not category:
            if use_callback and update.callback_query:
                await update.callback_query.edit_message_text(
                    "Error: No category selected. Please start over."
                )
            elif not use_callback and update.message:
                await update.message.reply_text(
                    "Error: No category selected. Please start over."
                )
            # Clear user data to allow new conversations
            if context.user_data:
                context.user_data.clear()
            return ConversationHandler.END

        tags = context.user_data.get(TikTokRecipeContextKey.TAGS, [])

        # Create the full Recipe object
        recipe_dto = RecipeDTO(**parsed_recipe_data)
        recipe = Recipe(
            title=recipe_dto.title,
            ingredients=recipe_dto.ingredients,
            steps=recipe_dto.steps,
            category=RecipeCategory(category),
            user_id=update.effective_user.id,
            tags=tags,
            desc=recipe_dto.desc,
            estimated_time=recipe_dto.estimated_time,
            notes=recipe_dto.notes,
            link=recipe_dto.link,
        )

        # Save to database
        recipe_repo: RecipeRepositoryABC = get_state()["recipe_repo"]
        saved_recipe = await recipe_repo.add(recipe)

        # instrumentation
        RECIPES_CREATED.labels(source=RecipeCreationSourceEnum.TIKTOK_AUTO).inc()

        # Show success message with recipe details
        success_message = f"{TIKTOK_SAVE_SUCCESS}\n\n{saved_recipe.to_md()}"
        if use_callback and update.callback_query and update.callback_query.message:
            await update.callback_query.edit_message_text(success_message)
            # Send the main keyboard in a separate message
            await context.bot.send_message(
                chat_id=update.callback_query.message.chat.id,
                text="What would you like to do next?",
                reply_markup=MAIN_KEYBOARD,
            )
        elif not use_callback and update.message:
            await update.message.reply_text(success_message)
            # Send the main keyboard in a separate message
            await context.bot.send_message(
                chat_id=update.message.chat.id,
                text="What would you like to do next?",
                reply_markup=MAIN_KEYBOARD,
            )

        # Clear user data to allow new conversations
        if context.user_data:
            context.user_data.clear()

        return ConversationHandler.END

    except Exception as e:
        error_message = f"Error saving recipe: {str(e)}"
        if use_callback and update.callback_query:
            await update.callback_query.edit_message_text(error_message)
        elif not use_callback and update.message:
            await update.message.reply_text(error_message)

        # Clear user data even on error
        if context.user_data:
            context.user_data.clear()

        return ConversationHandler.END


async def handle_manual_entry_choice(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle user's choice when TikTok parsing fails - offer manual entry or cancel."""
    # Create inline keyboard for user choice
    keyboard = [
        [InlineKeyboardButton("Fill Manually", callback_data="manual_entry")],
        [InlineKeyboardButton("Cancel", callback_data="cancel_manual")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(
            TIKTOK_PROCESSING_FAILED, reply_markup=reply_markup
        )
    return MANUAL_ENTRY


async def handle_manual_entry_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle callback from manual entry choice."""
    query = update.callback_query
    if not query:
        return MANUAL_ENTRY

    await query.answer()

    if query.data == "manual_entry":
        # User chose to continue with manual entry
        # Prepare data for add_recipe conversation and instruct user to use /add

        # Get the existing TikTok recipe data
        if not context.user_data:
            return ConversationHandler.END

        parsed_recipe_data = context.user_data.pop(
            TikTokRecipeContextKey.PARSED_RECIPE, {}
        )

        # Store TikTok data in a way that add_recipe can pick it up
        # We'll use a special key that persists across conversations
        context.user_data[TikTokRecipeContextKey.PENDING_TIKTOK_DATA] = {
            "tiktok_source": parsed_recipe_data,
            "from_tiktok": True,
        }

        # Create keyboard with button to start manual entry
        keyboard = [
            [
                InlineKeyboardButton(
                    "Start Manual Recipe Entry", callback_data="start_manual_entry"
                )
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            TIKTOK_MANUAL_ENTRY_PROMPT,
            reply_markup=reply_markup,
        )

        # End this conversation
        return ConversationHandler.END

    elif query.data == "cancel_manual":
        # User chose to cancel
        return await handle_cancel(update, context)

    return MANUAL_ENTRY


async def handle_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    if update.message:
        await update.message.reply_text(TIKTOK_CANCEL, reply_markup=MAIN_KEYBOARD)
    elif update.callback_query:
        await update.callback_query.edit_message_text(TIKTOK_CANCEL)

    # Clear user data
    if context.user_data:
        context.user_data.clear()

    return ConversationHandler.END
