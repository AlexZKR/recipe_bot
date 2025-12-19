"""Repository interface for recipe tag operations."""

from abc import ABC, abstractmethod

from recipebot.domain.recipe.recipe import RecipeTag


class RecipeTagRepositoryABC(ABC):
    """Abstract base class for recipe tag repository operations."""

    @abstractmethod
    async def get_user_tags(self, user_id: int) -> list[RecipeTag]:
        """Get all tags created by a user."""
        pass

    @abstractmethod
    async def create_tag(self, tag: RecipeTag) -> RecipeTag:
        """Create a new tag."""
        pass

    @abstractmethod
    async def get_or_create_tag(self, name: str, user_id: int) -> RecipeTag:
        """Get existing tag or create new one."""
        pass
