"""Shared callback parsing utilities for recipe CRUD operations."""


def parse_prefixed_callback(callback_data: str | None, prefix: str) -> str | None:
    """Parse callback data with a prefix.

    Args:
        callback_data: The callback data string
        prefix: The expected prefix (e.g., "recipe_", "edit_recipe_")

    Returns:
        The extracted value after the prefix, or None if invalid
    """
    if not callback_data or not isinstance(callback_data, str):
        return None

    if not callback_data.startswith(prefix):
        return None

    # Extract value: remove prefix
    value: str = callback_data[len(prefix) :]
    if not value:  # Ensure we have a non-empty value
        return None

    return value
