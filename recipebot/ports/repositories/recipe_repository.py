from abc import ABC, abstractmethod
from uuid import UUID

from recipebot.domain.recipe.recipe import Recipe


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
