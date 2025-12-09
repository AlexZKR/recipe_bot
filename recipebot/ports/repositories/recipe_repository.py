from abc import ABC, abstractmethod
from uuid import UUID

from recipebot.domain.recipe.recipe import Recipe, RecipeTag


class RecipeRepositoryABC(ABC):
    @abstractmethod
    async def add(self, recipe_data: Recipe) -> Recipe:
        pass

    @abstractmethod
    async def get(self, id: UUID) -> Recipe:
        pass

    @abstractmethod
    async def list_by_user(self, user_id: int) -> list[Recipe]:
        pass

    @abstractmethod
    async def update(self, recipe_data: Recipe) -> Recipe:
        pass

    @abstractmethod
    async def delete(self, id: UUID, user_id: int) -> None:
        pass

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

    @abstractmethod
    async def search_by_tags(self, user_id: int, tag_names: list[str]) -> list[Recipe]:
        """Search recipes by tags for a specific user."""
        pass
