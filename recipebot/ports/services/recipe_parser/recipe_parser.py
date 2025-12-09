from abc import ABC, abstractmethod

from recipebot.domain.recipe.recipe import RecipeDTO


class RecipeParserABC(ABC):
    """Parse recipe description."""

    @abstractmethod
    async def parse(self, description: str) -> RecipeDTO:
        pass
