from abc import ABC, abstractmethod

from recipebot.domain.recipe.recipe import Ingredient, RecipeDTO


class RecipeParserABC(ABC):
    """Parse recipe description."""

    @abstractmethod
    async def parse(self, description: str) -> RecipeDTO:
        """Parse recipe description, ingredients and steps from raw text with LLM."""
        pass

    @abstractmethod
    async def parse_ingredients(self, ingredients_text: str) -> list[Ingredient]:
        """Parse ingredients from raw text with LLM."""
        pass

    @abstractmethod
    async def parse_steps(self, steps_text: str) -> list[str]:
        """Parse steps from raw text with LLM."""
        pass
