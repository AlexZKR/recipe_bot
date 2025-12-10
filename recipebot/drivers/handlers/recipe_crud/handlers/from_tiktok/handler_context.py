"""Context keys for TikTok recipe handler."""

from enum import StrEnum


class TikTokRecipeContextKey(StrEnum):
    """Enum for TikTok recipe handler context keys."""

    TIKTOK_URL = "tiktok_url"
    PARSED_RECIPE = "parsed_recipe"
    PENDING_TIKTOK_DATA = "pending_tiktok_data"
    CATEGORY = "category"
    TAGS = "tags"
