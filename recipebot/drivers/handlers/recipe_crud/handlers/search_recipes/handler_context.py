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


class SearchRecipesCallbackPattern(StrEnum):
    """Enum for search recipes handler callback patterns."""

    RESULT_PREFIX = "search_result_"
    RESULT_PAGE_PREFIX = "search_page"
    RESULT_PAGINATED_PREFIX = "search_"

    TAG_PREFIX = "search_tag_"
    TAG_PAGE_PREFIX = "search_tag_page"

    MODE_PREFIX = "search_mode_"
