from telegram import ReplyKeyboardMarkup

# Define the main keyboard - shared across all handlers
MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [["/list", "/add", "/search"], ["/edit_recipe", "/delete_recipe"]],
    resize_keyboard=True,
    input_field_placeholder="Choose a command:",
)
