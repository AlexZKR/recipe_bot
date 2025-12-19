"""Context keys and callback patterns for search recipes handler."""

from enum import StrEnum


class SearchRecipesContextKey(StrEnum):
    """Enum for search recipes handler context keys."""

    SEARCH_TAGS = "search_tags"

    SELECTED_TAGS = "selected_tags"
    SELECTED_CATEGORIES = "selected_categories"


class SearchRecipesMode(StrEnum):
    """Enum for search recipes handler modes."""

    CATEGORY = "category"
    TAG = "tag"


class SearchRecipesFilterOperation(StrEnum):
    """Enum for filter selection operations in callbacks.

    Used for adding/removing filters of any type (tags, categories, etc.).
    """

    ADD = "add"
    REMOVE = "remove"


class SearchRecipesCallbackPattern(StrEnum):
    """Enum for search recipes handler callback patterns.

    Callback Format Reference:
    - Filter selection: {TAG_PREFIX}{operation}__{filter_value}__{page}
      Where operation is 'add' or 'remove' (see SearchRecipesFilterOperation)
      Uses double underscores (__) as delimiter to avoid conflicts with tag names
      Tag names must NOT contain '__' (double underscores)
      Examples:
        - 'search_tag_add__easy__1' (tag: 'easy')
        - 'search_tag_remove__not_selected__2' (tag: 'not_selected')

    - Tag pagination: {TAG_PAGE_PREFIX}{page_number}
      Example: 'search_tag_page_2'

    - Mode selection: {MODE_PREFIX}{mode}
      Example: 'search_mode_tag', 'search_mode_category'
    """

    RESULT_PREFIX = "search_result_"
    RESULT_PAGE_PREFIX = "search_page"
    RESULT_PAGINATED_PREFIX = "search_"

    TAG_PREFIX = "search_tag_"
    TAG_PAGE_PREFIX = "search_tag_page"

    MODE_PREFIX = "search_mode_"
