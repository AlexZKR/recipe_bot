"""Context keys for delete recipe handler."""

from enum import StrEnum


class DeleteRecipeContextKey(StrEnum):
    """Enum for delete recipe handler context keys."""

    RECIPE_TO_DELETE = "recipe_to_delete"
