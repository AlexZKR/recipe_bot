from abc import ABC, abstractmethod

from recipebot.ports.services.recipe_parser.schemas import RecipeDTO


class RecipeParserABC(ABC):
    """Parse recipe description."""

    @abstractmethod
    async def parse(self, description: str) -> RecipeDTO:
        pass
