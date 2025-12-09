from recipebot.domain.recipe.recipe import RecipeDTO
from recipebot.ports.services.recipe_parser import RecipeParserABC
from recipebot.ports.services.tt_resolver import TTResolverABC


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
        recipe_dto = await self.recipe_parser.parse(resolution_result.description)
        recipe_dto.link = resolution_result.source_url
        return recipe_dto
