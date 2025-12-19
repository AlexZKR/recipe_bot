from urllib.parse import urlparse

from telegram.ext import ContextTypes


def add_tag_to_recipe(context: ContextTypes.DEFAULT_TYPE, tag_name: str) -> bool:
    """Add a tag to the current recipe being created."""
    if not context.user_data:
        return False

    # Validate tag name - forbid double underscores used as callback delimiters
    if "__" in tag_name:
        # Tag names cannot contain double underscores as they're used as delimiters in callbacks
        return False

    current_tags = context.user_data.get("tags", [])
    if tag_name not in current_tags:
        current_tags.append(tag_name)
        context.user_data["tags"] = current_tags

    return True


def validate_source_link(source_link: str) -> bool:
    """Validate if the source link is a valid URL."""
    try:
        result = urlparse(source_link)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
