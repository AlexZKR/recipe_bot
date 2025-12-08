from logging import getLogger
from uuid import UUID

from recipebot.adapters.repositories.sql.base.base_asyncpg_repo import AsyncpgConnection
from recipebot.adapters.repositories.sql.base.utils import load_query
from recipebot.adapters.repositories.sql.recipe.queries import (
    GET_RECIPE_BY_ID_QUERY,
    GET_RECIPES_BY_USER_QUERY,
    INSERT_RECIPE_QUERY,
    UPDATE_RECIPE_QUERY,
)
from recipebot.domain.recipe.recipe import Recipe
from recipebot.ports.repositories.exceptions import RecipeNotFound, RepositoryException
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
            if not row:
                raise RepositoryException("Recipe not created")
        return Recipe.model_validate(dict(row))

    async def get(self, id: UUID) -> Recipe:
        logger.info(f"Getting recipe {id}")
        async with self.conn.get_cursor() as conn:
            row = await conn.fetchrow(
                load_query(__file__, GET_RECIPE_BY_ID_QUERY),
                id,
            )

        if not row:
            raise RecipeNotFound(f"Recipe with ID {id} not found")

        return Recipe.model_validate(dict(row))

    async def list_by_user(self, user_id: int) -> list[Recipe]:
        logger.info(f"Listing recipes for user {user_id}")
        async with self.conn.get_cursor() as conn:
            rows = await conn.fetch(
                load_query(__file__, GET_RECIPES_BY_USER_QUERY),
                user_id,
            )
        return [Recipe.model_validate(dict(row)) for row in rows]

    async def update(self, recipe_data: Recipe) -> Recipe:
        logger.info(f"Updating recipe {recipe_data.id} for user {recipe_data.user_id}")
        async with self.conn.get_cursor() as conn:
            row = await conn.fetchrow(
                load_query(__file__, UPDATE_RECIPE_QUERY),
                recipe_data.title,
                recipe_data.ingredients,
                recipe_data.steps,
                recipe_data.category.value,
                recipe_data.servings,
                recipe_data.description,
                recipe_data.estimated_time,
                recipe_data.notes,
                str(recipe_data.link) if recipe_data.link else None,
                recipe_data.id,
                recipe_data.user_id,
            )
        if not row:
            raise RecipeNotFound(f"Recipe with ID {recipe_data.id} not found")
        return Recipe.model_validate(dict(row))
