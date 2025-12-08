"""Generic pagination utilities for recipe CRUD operations."""

from collections.abc import Callable
from typing import Any

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from recipebot.config import settings


class PaginatedResult:
    """Represents a paginated result set."""

    def __init__(
        self,
        items: list[Any],
        page: int,
        page_size: int | None = None,
        callback_prefix: str = "",
    ):
        self.items = items
        self.page = page
        self.page_size = page_size or settings.APP.recipe_page_size
        self.callback_prefix = callback_prefix

        self.total_items = len(items)
        self.total_pages = (self.total_items + self.page_size - 1) // self.page_size

        # Ensure page is within bounds
        if self.page < 1:
            self.page = 1
        elif self.page > self.total_pages:
            self.page = self.total_pages

    @property
    def start_index(self) -> int:
        """Get the start index for the current page."""
        return (self.page - 1) * self.page_size

    @property
    def end_index(self) -> int:
        """Get the end index for the current page."""
        return min(self.start_index + self.page_size, self.total_items)

    @property
    def current_page_items(self) -> list[Any]:
        """Get items for the current page."""
        return self.items[self.start_index : self.end_index]

    @property
    def has_previous(self) -> bool:
        """Check if there's a previous page."""
        return self.page > 1

    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self.page < self.total_pages

    def get_page_info_text(self) -> str:
        """Get page information text."""
        if self.total_pages <= 1:
            return f"Total: {self.total_items} recipes"

        return (
            f"Page {self.page}/{self.total_pages} "
            f"(showing {len(self.current_page_items)} of {self.total_items} recipes)"
        )


def create_paginated_keyboard(
    paginated_result: PaginatedResult,
    item_callback_factory: Callable[[Any, int], str],
    navigation_prefix: str = "page",
) -> InlineKeyboardMarkup:
    """Create a paginated inline keyboard.

    Args:
        paginated_result: The paginated result object
        item_callback_factory: Function that creates callback data for each item
        navigation_prefix: Prefix for navigation buttons (e.g., 'page', 'delete_page')

    Returns:
        InlineKeyboardMarkup with items and navigation buttons
    """
    keyboard = []

    # Add current page items
    for item in paginated_result.current_page_items:
        keyboard.append(
            [
                InlineKeyboardButton(
                    item.title,
                    callback_data=item_callback_factory(item, paginated_result.page),
                )
            ]
        )

    # Add navigation buttons if needed
    if paginated_result.total_pages > 1:
        nav_buttons = []

        if paginated_result.has_previous:
            nav_buttons.append(
                InlineKeyboardButton(
                    "⬅️ Previous",
                    callback_data=f"{navigation_prefix}_{paginated_result.page - 1}",
                )
            )

        # Page info is shown in message text, not as button

        if paginated_result.has_next:
            nav_buttons.append(
                InlineKeyboardButton(
                    "Next ➡️",
                    callback_data=f"{navigation_prefix}_{paginated_result.page + 1}",
                )
            )

        if nav_buttons:
            keyboard.append(nav_buttons)

    return InlineKeyboardMarkup(keyboard)


def parse_pagination_callback(callback_data: str, prefix: str = "page") -> int | None:
    """Parse pagination callback data.

    Args:
        callback_data: Callback data (e.g., 'page_2', 'delete_page_3')
        prefix: The pagination prefix to look for

    Returns:
        Page number or None if not a pagination callback
    """
    if not callback_data.startswith(f"{prefix}_"):
        return None

    try:
        page_str = callback_data[len(f"{prefix}_") :]
        return int(page_str)
    except ValueError:
        return None
