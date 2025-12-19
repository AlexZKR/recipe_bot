from abc import ABC, abstractmethod
from uuid import UUID

from recipebot.adapters.repositories.sql.recipe.recipe_filters import RecipeFilters
from recipebot.domain.recipe.recipe import Recipe


class RecipeRepositoryABC(ABC):
    @abstractmethod
    async def add(self, recipe_data: Recipe) -> Recipe:
        pass

    @abstractmethod
    async def get(self, id: UUID) -> Recipe:
        pass

    @abstractmethod
    async def list_filtered(self, filters: RecipeFilters) -> list[Recipe]:
        """List recipes with optional filtering by tags and categories."""
        pass

    @abstractmethod
    async def update(self, recipe_data: Recipe) -> Recipe:
        pass

    @abstractmethod
    async def delete(self, id: UUID, user_id: int) -> None:
        pass
