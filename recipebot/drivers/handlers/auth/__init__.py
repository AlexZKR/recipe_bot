from telegram.ext import CommandHandler

from recipebot.drivers.handlers.auth.handlers import for_registered, register

start_handler = CommandHandler("register", register)
registered_handler = CommandHandler("is_registered", for_registered)
