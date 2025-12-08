from recipebot.drivers.handlers.recipe_crud.handlers.delete_recipe.constants import (
    DELETE_FIELD_MIN_PARTS,
    DELETE_RECIPE_PREFIX,
)
from recipebot.drivers.handlers.recipe_crud.shared.callbacks import (
    parse_prefixed_callback,
)


def parse_delete_recipe_callback(callback_data: str | None) -> str | None:
    """Parse delete recipe callback data.

    Args:
        callback_data: Callback data in format "delete_recipe_{recipe_id}"

    Returns:
        recipe_id string or None if invalid
    """
    return parse_prefixed_callback(callback_data, DELETE_RECIPE_PREFIX)


def parse_delete_confirm_callback(callback_data: str | None) -> tuple[str, str] | None:
    """Parse delete confirmation callback data.

    Args:
        callback_data: Callback data in format "delete_confirm_{recipe_id}_{choice}"

    Returns:
        Tuple of (recipe_id, choice) or None if invalid
    """
    if not callback_data or not isinstance(callback_data, str):
        return None

    if not callback_data.startswith("delete_confirm_"):
        return None

    parts = callback_data.split("_")
    if len(parts) < DELETE_FIELD_MIN_PARTS:
        return None

    recipe_id = parts[2]
    choice = parts[3]

    if not recipe_id or choice not in ["yes", "no"]:
        return None

    return recipe_id, choice
