from uuid import UUID

import orjson
import structlog

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

logger: structlog.BoundLogger = structlog.get_logger(__name__)


class RecipeAsyncpgRepo(RecipeRepositoryABC):
    def __init__(
        self, conn: AsyncpgConnection, tag_repo: RecipeTagRepositoryABC
    ) -> None:
        self.conn = conn
        self.tag_repo = tag_repo

    async def add(self, recipe_data: Recipe) -> Recipe:
        try:
            bound_logger = logger.bind(recipe_id=recipe_data.id)
            bound_logger.info("Adding recipe")

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
                    orjson.dumps(
                        [
                            ingredient.model_dump()
                            for ingredient in recipe_data.ingredients
                        ]
                    ),
                    orjson.dumps(recipe_data.steps),
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
        except Exception as exc:
            bound_logger.exception("Error adding recipe", exc_info=True)
            raise exc

    async def get(self, id: UUID) -> Recipe:
        try:
            bound_logger = logger.bind(recipe_id=id)
            bound_logger.info("Getting recipe")

            async with self.conn.get_cursor() as conn:
                row = await conn.fetchrow(
                    load_query(__file__, GET_RECIPE_BY_ID_QUERY),
                    id,
                )

                if not row:
                    raise RecipeNotFound(recipe_id=id)

            # Convert tag_names array to list of strings for display
            row_dict = dict(row)
            if row_dict.get("tag_names"):
                row_dict["tags"] = [
                    tag for tag in row_dict["tag_names"] if tag is not None
                ]
            else:
                row_dict["tags"] = []

            # Convert ingredients JSONB back to list of Ingredient objects
            if row_dict.get("ingredients"):
                ingredients_data = orjson.loads(row_dict["ingredients"])
                row_dict["ingredients"] = ingredients_data

            # Convert steps JSONB back to list of strings
            if row_dict.get("steps"):
                steps_data = orjson.loads(row_dict["steps"])
                row_dict["steps"] = steps_data

            return Recipe.model_validate(row_dict)
        except Exception as exc:
            bound_logger.exception("Error getting recipe", exc_info=True)
            raise exc

    async def list_filtered(self, filters: RecipeFilters) -> list[Recipe]:
        """List recipes with optional filtering by tags and categories."""
        try:
            bound_logger = logger.bind(filters=filters.model_dump_json())
            bound_logger.info("Listing recipes")

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
                    ingredients_data = orjson.loads(row_dict["ingredients"])
                    row_dict["ingredients"] = ingredients_data

                # Convert steps JSONB back to list of strings
                if row_dict.get("steps"):
                    steps_data = orjson.loads(row_dict["steps"])
                    row_dict["steps"] = steps_data

                recipes.append(Recipe.model_validate(row_dict))

            return recipes
        except Exception as exc:
            bound_logger.exception("Error listing recipes", exc_info=True)
            raise exc

    async def update(self, recipe_data: Recipe) -> Recipe:
        try:
            bound_logger = logger.bind(recipe_id=recipe_data.id)
            bound_logger.info("Updating recipe")

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
                    orjson.dumps(
                        [
                            ingredient.model_dump()
                            for ingredient in recipe_data.ingredients
                        ]
                    ),
                    orjson.dumps(recipe_data.steps),
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
                raise RecipeNotFound(recipe_id=recipe_data.id)
            return Recipe.model_validate(dict(row))
        except Exception as exc:
            bound_logger.exception("Error updating recipe", exc_info=True)
            raise exc

    async def delete(self, id: UUID, user_id: int) -> None:
        try:
            bound_logger = logger.bind(recipe_id=id)
            bound_logger.info("Deleting recipe")
            async with self.conn.get_cursor() as conn:
                result = await conn.execute(
                    load_query(__file__, DELETE_RECIPE_QUERY),
                    id,
                    user_id,
                )
                if result == "DELETE 0":
                    raise RecipeNotFound(recipe_id=id)
        except Exception as exc:
            bound_logger.exception("Error deleting recipe", exc_info=True)
            raise exc
