# This file is deprecated - use shared utilities instead
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from recipebot.drivers.handlers.recipe_crud.handlers.add_recipe.constants import (
    ADD_TAGS,
)
from recipebot.drivers.state import get_state

TAGS_PER_ROW = 3


async def show_tags_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show keyboard with existing tags and option to add new."""
    if not update.effective_user:
        return

    # Get existing tags for user
    tag_repo = get_state()["tag_repo"]
    existing_tags = await tag_repo.get_user_tags(update.effective_user.id)

    # Get already selected tags for this recipe
    selected_tags = set(context.user_data.get("tags", []) if context.user_data else [])

    # Create keyboard with existing tags (excluding already selected) + "Add New Tag" option
    keyboard = []
    row = []

    # Add existing tags that haven't been selected yet
    for tag in existing_tags:
        if tag.name not in selected_tags:
            row.append(
                InlineKeyboardButton(f"#{tag.name}", callback_data=f"tag_{tag.name}")
            )
            if len(row) == TAGS_PER_ROW:
                keyboard.append(row)
                row = []

    if row:  # Add remaining buttons
        keyboard.append(row)

    # Add "Add New Tag" and "Done" buttons
    keyboard.append(
        [
            InlineKeyboardButton("➕ Add New Tag", callback_data="new_tag"),
            InlineKeyboardButton("✅ Done", callback_data="tags_done"),
        ]
    )

    # Get current tags for display
    current_tags = context.user_data.get("tags", []) if context.user_data else []
    if current_tags:
        tags_str = ", ".join(f"#{tag}" for tag in current_tags)
        message_text = f"Add tags to your recipe (optional). Current tags: {tags_str}. Select from existing tags or type a new one:"  # nosec B608
    else:
        message_text = ADD_TAGS

    # Send or edit message based on context
    if hasattr(update, "callback_query") and update.callback_query:
        await update.callback_query.edit_message_text(
            message_text, reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif update.message:
        await update.message.reply_text(
            message_text, reply_markup=InlineKeyboardMarkup(keyboard)
        )
