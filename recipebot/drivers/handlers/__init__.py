from telegram.ext._application import Application

from recipebot.drivers.handlers.auth import registered_handler, start_handler
from recipebot.drivers.handlers.recipe.handlers import add_recipe_handler


def add_handlers(app: Application) -> None:
    app.add_handler(start_handler)
    app.add_handler(registered_handler)
    app.add_handler(add_recipe_handler)
