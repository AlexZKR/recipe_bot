from logging import getLogger

from recipebot.adapters.repositories.sql.base.base_asyncpg_repo import AsyncpgConnection
from recipebot.adapters.repositories.sql.base.utils import load_query
from recipebot.adapters.repositories.sql.recipe.queries import INSERT_RECIPE_QUERY
from recipebot.domain.recipe.recipe import Recipe
from recipebot.ports.repositories.recipe_repository import RecipeRepositoryABC

logger = getLogger(__name__)


class RecipeAsyncpgRepo(RecipeRepositoryABC):
    def __init__(self, conn: AsyncpgConnection) -> None:
        self.conn = conn

    async def add(self, recipe_data: Recipe) -> Recipe:
        logger.info(f"Adding recipe {recipe_data.title} for user {recipe_data.user_id}")
        async with self.conn.get_cursor() as conn:
            row = await conn.fetchrow(
                load_query(__file__, INSERT_RECIPE_QUERY),
                recipe_data.id,
                recipe_data.title,
                recipe_data.ingredients,
                recipe_data.steps,
                recipe_data.category.value,
                recipe_data.description,
                recipe_data.estimated_time,
                recipe_data.servings,
                recipe_data.notes,
                str(recipe_data.link) if recipe_data.link else None,
                recipe_data.user_id,
            )
        return Recipe.model_validate(row)
