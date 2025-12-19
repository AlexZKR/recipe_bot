import json
from logging import getLogger
from uuid import UUID

from recipebot.adapters.repositories.sql.base.base_asyncpg_repo import AsyncpgConnection
from recipebot.adapters.repositories.sql.base.utils import load_query
from recipebot.adapters.repositories.sql.recipe.queries import (
    DELETE_RECIPE_QUERY,
    GET_RECIPE_BY_ID_QUERY,
    INSERT_RECIPE_QUERY,
    SEARCH_RECIPES_FILTERED_QUERY,
    UPDATE_RECIPE_QUERY,
)
from recipebot.adapters.repositories.sql.recipe.recipe_filters import RecipeFilters
from recipebot.domain.recipe.recipe import Recipe
from recipebot.ports.repositories.exceptions import RecipeNotFound, RepositoryException
from recipebot.ports.repositories.recipe_repository import RecipeRepositoryABC
from recipebot.ports.repositories.recipe_tag_repository import RecipeTagRepositoryABC

logger = getLogger(__name__)


class RecipeAsyncpgRepo(RecipeRepositoryABC):
    def __init__(
        self, conn: AsyncpgConnection, tag_repo: RecipeTagRepositoryABC
    ) -> None:
        self.conn = conn
        self.tag_repo = tag_repo

    async def add(self, recipe_data: Recipe) -> Recipe:
        logger.info(f"Adding recipe {recipe_data.title} for user {recipe_data.user_id}")

        # Convert tag names to tag IDs for database storage
        tag_ids = []
        if recipe_data.tags:
            for tag_name in recipe_data.tags:
                tag = await self.tag_repo.get_or_create_tag(
                    tag_name, recipe_data.user_id
                )
                tag_ids.append(tag.id)

        async with self.conn.get_cursor() as conn:
            row = await conn.fetchrow(
                load_query(__file__, INSERT_RECIPE_QUERY),
                recipe_data.id,
                recipe_data.title,
                json.dumps(
                    [ingredient.model_dump() for ingredient in recipe_data.ingredients]
                ),
                json.dumps(recipe_data.steps),
                recipe_data.category.value,
                recipe_data.desc,
                recipe_data.estimated_time,
                recipe_data.servings,
                recipe_data.notes,
                str(recipe_data.link) if recipe_data.link else None,
                recipe_data.user_id,
                tag_ids,
            )
            if not row:
                raise RepositoryException("Recipe not created")

            # Get the created recipe with proper tag names
            recipe_id = row["id"]
            return await self.get(recipe_id)

    async def get(self, id: UUID) -> Recipe:
        logger.info(f"Getting recipe {id}")
        async with self.conn.get_cursor() as conn:
            row = await conn.fetchrow(
                load_query(__file__, GET_RECIPE_BY_ID_QUERY),
                id,
            )

        if not row:
            raise RecipeNotFound(f"Recipe with ID {id} not found")

        # Convert tag_names array to list of strings for display
        row_dict = dict(row)
        if row_dict.get("tag_names"):
            row_dict["tags"] = [tag for tag in row_dict["tag_names"] if tag is not None]
        else:
            row_dict["tags"] = []

        # Convert ingredients JSONB back to list of Ingredient objects
        if row_dict.get("ingredients"):
            ingredients_data = json.loads(row_dict["ingredients"])
            row_dict["ingredients"] = ingredients_data

        # Convert steps JSONB back to list of strings
        if row_dict.get("steps"):
            steps_data = json.loads(row_dict["steps"])
            row_dict["steps"] = steps_data

        return Recipe.model_validate(row_dict)

    async def list_filtered(self, filters: RecipeFilters) -> list[Recipe]:
        """List recipes with optional filtering by tags and categories."""
        logger.info(str(filters))

        async with self.conn.get_cursor() as conn:
            result = await conn.fetch(
                load_query(__file__, SEARCH_RECIPES_FILTERED_QUERY),
                filters.user_id,
                filters.tag_names,
                filters.category_names,
            )

        recipes = []
        for row in result:
            row_dict = dict(row)
            if row_dict.get("tag_names"):
                row_dict["tags"] = [
                    tag for tag in row_dict["tag_names"] if tag is not None
                ]
            else:
                row_dict["tags"] = []

            # Convert ingredients JSONB back to list of Ingredient objects
            if row_dict.get("ingredients"):
                ingredients_data = json.loads(row_dict["ingredients"])
                row_dict["ingredients"] = ingredients_data

            # Convert steps JSONB back to list of strings
            if row_dict.get("steps"):
                steps_data = json.loads(row_dict["steps"])
                row_dict["steps"] = steps_data

            recipes.append(Recipe.model_validate(row_dict))

        return recipes

    async def update(self, recipe_data: Recipe) -> Recipe:
        logger.info(f"Updating recipe {recipe_data.id} for user {recipe_data.user_id}")

        # Convert tag names to tag IDs for database storage
        tag_ids = []
        if recipe_data.tags:
            for tag_name in recipe_data.tags:
                tag = await self.tag_repo.get_or_create_tag(
                    tag_name, recipe_data.user_id
                )
                tag_ids.append(tag.id)

        async with self.conn.get_cursor() as conn:
            row = await conn.fetchrow(
                load_query(__file__, UPDATE_RECIPE_QUERY),
                recipe_data.title,
                json.dumps(
                    [ingredient.model_dump() for ingredient in recipe_data.ingredients]
                ),
                json.dumps(recipe_data.steps),
                recipe_data.category.value,
                recipe_data.servings,
                recipe_data.desc,
                recipe_data.estimated_time,
                recipe_data.notes,
                str(recipe_data.link) if recipe_data.link else None,
                tag_ids,
                recipe_data.id,
                recipe_data.user_id,
            )
        if not row:
            raise RecipeNotFound(f"Recipe with ID {recipe_data.id} not found")
        return Recipe.model_validate(dict(row))

    async def delete(self, id: UUID, user_id: int) -> None:
        logger.info(f"Deleting recipe {id} for user {user_id}")
        async with self.conn.get_cursor() as conn:
            result = await conn.execute(
                load_query(__file__, DELETE_RECIPE_QUERY),
                id,
                user_id,
            )
            if result == "DELETE 0":
                raise RecipeNotFound(f"Recipe with ID {id} not found or access denied")
