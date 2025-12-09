from recipebot.adapters.services.groq_tt_parser.tt_recipe_prompt import (
    get_tt_recipe_prompt,
)
from recipebot.config import settings
from recipebot.domain.recipe.recipe import RecipeDTO
from recipebot.infra.groq.client import GroqClient
from recipebot.ports.services.recipe_parser.recipe_parser import RecipeParserABC


class GroqTTRecipeParser(RecipeParserABC):
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
