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
        """String representation of the filters."""
        return f"{self.model_dump_json()}"
