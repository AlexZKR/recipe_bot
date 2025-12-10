import logging

from recipebot.domain.recipe.recipe import RecipeDTO
from recipebot.ports.services.recipe_parser import RecipeParserABC
from recipebot.ports.services.tt_resolver import ResolutionResult, TTResolverABC

logger = logging.getLogger(__name__)


class RecipeFromTTTask:
    def __init__(
        self,
        tt_resolver: TTResolverABC,
        recipe_parser: RecipeParserABC,
    ):
        self.tt_resolver = tt_resolver
        self.recipe_parser = recipe_parser

    async def run(self, url: str) -> RecipeDTO:
        resolution_result = await self.tt_resolver.resolve(url)
        if resolution_result.description is None:
            logger.info("No description found in TikTok URL")
            return self._handle_no_description(resolution_result)

        recipe_dto = await self.recipe_parser.parse(resolution_result.description)
        recipe_dto.link = resolution_result.source_url
        return recipe_dto

    def _handle_no_description(self, resolution_result: ResolutionResult) -> RecipeDTO:
        return RecipeDTO(
            title="No title found in TikTok URL",
            desc="No description found in TikTok URL",
            link=resolution_result.source_url,
            ingredients=[],
            steps=[],
            servings=None,
            estimated_time=None,
            notes=None,
        )
