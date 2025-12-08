"""Shared utilities for recipe CRUD operations."""

from recipebot.drivers.handlers.recipe_crud.shared.callbacks import (
    parse_prefixed_callback,
)
from recipebot.drivers.handlers.recipe_crud.shared.constants import (
    RECIPE_PREFIX,
)
from recipebot.drivers.handlers.recipe_crud.shared.keyboards import (
    create_category_reply_keyboard,
    create_recipe_selection_keyboard,
)
from recipebot.drivers.handlers.recipe_crud.shared.pagination import (
    PaginatedResult,
    create_paginated_keyboard,
    parse_pagination_callback,
)

__all__ = [
    # Callbacks
    "parse_prefixed_callback",
    # Constants
    "RECIPE_PREFIX",
    # Keyboards
    "create_recipe_selection_keyboard",
    "create_category_reply_keyboard",
    # Pagination
    "PaginatedResult",
    "create_paginated_keyboard",
    "parse_pagination_callback",
]
