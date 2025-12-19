"""Recipe filtering criteria."""

from pydantic import BaseModel


class RecipeFilters(BaseModel):
    """Filtering criteria for recipe queries."""

    user_id: int
    tag_names: list[str] | None = None
    category_names: list[str] | None = None

    def has_filters(self) -> bool:
        """Check if any filters are applied."""
        return bool(self.tag_names or self.category_names)

    def __str__(self) -> str:
        """String representation of the filters for logging."""
        parts = [f"user {self.user_id}"]
        if self.tag_names:
            parts.append(f"tags={self.tag_names}")
        if self.category_names:
            parts.append(f"categories={self.category_names}")
        return f"Listing recipes for {' with '.join(parts)}"
