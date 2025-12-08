# Conversation states for field editing
(
    EDITING_TITLE,
    EDITING_INGREDIENTS,
    EDITING_STEPS,
    EDITING_CATEGORY,
    EDITING_SERVINGS,
    EDITING_DESCRIPTION,
    EDITING_TIME,
    EDITING_NOTES,
    EDITING_LINK,
) = range(9)

# Callback data parsing constants
EDIT_FIELD_MIN_PARTS = 4

# Callback data prefixes
EDIT_RECIPE_PREFIX = "edit_recipe_"

# Field names
EDITABLE_FIELDS = [
    "title",
    "ingredients",
    "steps",
    "category",
    "servings",
    "description",
    "estimated_time",
    "notes",
    "link",
]
