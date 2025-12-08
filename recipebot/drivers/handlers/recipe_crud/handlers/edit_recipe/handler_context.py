"""Context keys for edit recipe handler."""

from enum import StrEnum


class EditRecipeContextKey(StrEnum):
    """Enum for edit recipe handler context keys."""

    EDITING_RECIPE = "editing_recipe"
    EDITING_FIELD = "editing_field"
