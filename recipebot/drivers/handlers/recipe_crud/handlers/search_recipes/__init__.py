from telegram.ext import CallbackQueryHandler, CommandHandler

from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.category_search.category_handlers import (
    handle_category_pagination,
    handle_category_selection,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.handler import (
    handle_search_mode_selection,
    search_recipes_handler,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.handler_context import (
    SearchRecipesCallbackPattern,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.search_results import (
    handle_search_pagination,
    handle_search_result,
)
from recipebot.drivers.handlers.recipe_crud.handlers.search_recipes.tag_search.tag_handlers import (
    handle_tag_pagination,
    handle_tag_selection,
)

search_recipes_handler = CommandHandler("search", search_recipes_handler)
search_mode_selection_handler = CallbackQueryHandler(
    handle_search_mode_selection,
    pattern=rf"^{SearchRecipesCallbackPattern.MODE_PREFIX}",
)
search_tag_selection_handler = CallbackQueryHandler(
    handle_tag_selection, pattern=rf"^{SearchRecipesCallbackPattern.TAG_PREFIX}"
)
search_category_selection_handler = CallbackQueryHandler(
    handle_category_selection, pattern=r"^search_category_"
)

search_result_handler = CallbackQueryHandler(
    handle_search_result,
    pattern=rf"^{SearchRecipesCallbackPattern.RESULT_PREFIX}[0-9a-f\-]+$",
)
search_pagination_handler = CallbackQueryHandler(
    handle_search_pagination,
    pattern=rf"^{SearchRecipesCallbackPattern.RESULT_PAGE_PREFIX}_",
)
search_tag_pagination_handler = CallbackQueryHandler(
    handle_tag_pagination, pattern=rf"^{SearchRecipesCallbackPattern.TAG_PAGE_PREFIX}_"
)
search_category_pagination_handler = CallbackQueryHandler(
    handle_category_pagination, pattern=r"^search_category_page_"
)
