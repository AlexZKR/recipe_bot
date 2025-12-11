from enum import StrEnum

from prometheus_client import Counter


class RecipeCreationSourceEnum(StrEnum):
    TIKTOK_AUTO = "tiktok_auto"
    TIKTOK_MANUAL = "tiktok_manual"
    MANUAL = "manual"


RECIPES_CREATED = Counter(
    "recipebot_recipes_created_total",
    "Total number of recipes created by users",
    ["source"],
)
