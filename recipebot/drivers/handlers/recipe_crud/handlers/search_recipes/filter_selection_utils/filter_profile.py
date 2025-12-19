"""Base filter profile configuration."""

from collections.abc import Awaitable, Callable
from typing import Any

from pydantic import BaseModel


class FilterProfile(BaseModel):
    """Configuration profile for filter selection functionality.

    Encapsulates all the settings needed for a specific filter type
    (tags, categories, etc.) to work with the generic filter selection system.
    """

    # Data access
    item_getter: Callable[[int], Awaitable[list[Any]]]

    # User data storage
    selected_user_data_key: str

    # Callback prefixes
    callback_prefix: str
    page_prefix: str

    # UI configuration
    item_type: str  # "tags", "categories", etc.
    back_callback_data: str

    # Display options
    show_main_keyboard: bool = True
