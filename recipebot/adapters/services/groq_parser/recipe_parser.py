from recipebot.adapters.services.groq_parser.prompts.ingredients import (
    get_tt_recipe_ingredients_prompt,
)
from recipebot.adapters.services.groq_parser.prompts.steps import (
    get_tt_recipe_steps_prompt,
)
from recipebot.adapters.services.groq_parser.prompts.tt_recipe_prompt import (
    get_tt_recipe_prompt,
)
from recipebot.adapters.services.groq_parser.schemas import (
    IngredientsExtractionSchema,
    StepsExtractionSchema,
)
from recipebot.config import settings
from recipebot.domain.recipe.recipe import Ingredient, RecipeDTO
from recipebot.infra.groq.client import GroqClient
from recipebot.ports.services.recipe_parser.recipe_parser import RecipeParserABC


class GroqRecipeParser(RecipeParserABC):
    def __init__(self, groq_client: GroqClient):
        self.groq_client = groq_client

    async def parse(self, description: str) -> RecipeDTO:
        prompt = get_tt_recipe_prompt(description)
        dto = await self.groq_client.get_json_structured_output_completion(
            model=settings.TIKTOK_DESCRIPTION_PARSE_SETTINGS.model,
            messages=prompt,
            schema=RecipeDTO,
            schema_name="RecipeDTO",
        )
        return dto

    async def parse_ingredients(self, ingredients_text: str) -> list[Ingredient]:
        prompt = get_tt_recipe_ingredients_prompt(ingredients_text)
        ingredients = await self.groq_client.get_json_structured_output_completion(
            model=settings.TIKTOK_DESCRIPTION_PARSE_SETTINGS.model,
            messages=prompt,
            schema=IngredientsExtractionSchema,
            schema_name="Ingredients",
        )
        return ingredients.ingredients

    async def parse_steps(self, steps_text: str) -> list[str]:
        prompt = get_tt_recipe_steps_prompt(steps_text)
        steps = await self.groq_client.get_json_structured_output_completion(
            model=settings.TIKTOK_DESCRIPTION_PARSE_SETTINGS.model,
            messages=prompt,
            schema=StepsExtractionSchema,
            schema_name="Steps",
        )
        return steps.steps
