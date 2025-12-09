from recipebot.drivers.handlers.recipe_crud.shared.callbacks import (
    parse_prefixed_callback,
)


def parse_recipe_callback(callback_data: str | None) -> str | None:
    """Parse recipe callback data.

    Args:
        callback_data: Callback data in format "recipe_{recipe_id}"

    Returns:
        recipe_id string or None if invalid
    """
    return parse_prefixed_callback(callback_data, "recipe_")
