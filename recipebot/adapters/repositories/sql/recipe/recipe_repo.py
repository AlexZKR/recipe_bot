import json
from logging import getLogger
from uuid import UUID

from recipebot.adapters.repositories.sql.base.base_asyncpg_repo import AsyncpgConnection
from recipebot.adapters.repositories.sql.base.utils import load_query
from recipebot.adapters.repositories.sql.recipe.queries import (
    CREATE_TAG_QUERY,
    DELETE_RECIPE_QUERY,
    FIND_EXISTING_TAG_QUERY,
    GET_RECIPE_BY_ID_QUERY,
    GET_RECIPES_BY_USER_QUERY,
    GET_USER_TAGS_QUERY,
    INSERT_RECIPE_QUERY,
    SEARCH_RECIPES_BY_TAGS_QUERY,
    UPDATE_RECIPE_QUERY,
)
from recipebot.domain.recipe.recipe import Recipe, RecipeTag
from recipebot.ports.repositories.exceptions import RecipeNotFound, RepositoryException
from recipebot.ports.repositories.recipe_repository import RecipeRepositoryABC

logger = getLogger(__name__)


class RecipeAsyncpgRepo(RecipeRepositoryABC):
    def __init__(self, conn: AsyncpgConnection) -> None:
        self.conn = conn

    async def add(self, recipe_data: Recipe) -> Recipe:
        logger.info(f"Adding recipe {recipe_data.title} for user {recipe_data.user_id}")

        # Convert tag names to tag IDs for database storage
        tag_ids = []
        if recipe_data.tags:
            for tag_name in recipe_data.tags:
                tag = await self.get_or_create_tag(tag_name, recipe_data.user_id)
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

    async def list_by_user(self, user_id: int) -> list[Recipe]:
        logger.info(f"Listing recipes for user {user_id}")
        async with self.conn.get_cursor() as conn:
            result = await conn.fetch(
                load_query(__file__, GET_RECIPES_BY_USER_QUERY),
                user_id,
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
                tag = await self.get_or_create_tag(tag_name, recipe_data.user_id)
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

    async def get_user_tags(self, user_id: int) -> list[RecipeTag]:
        """Get all tags created by a user."""
        async with self.conn.get_cursor() as conn:
            result = await conn.fetch(
                load_query(__file__, GET_USER_TAGS_QUERY),
                user_id,
            )
            return [
                RecipeTag(
                    id=row["id"],
                    name=row["name"],
                    group_id=row["group_id"],
                    user_id=row["user_id"],
                )
                for row in result
            ]

    async def create_tag(self, tag: RecipeTag) -> RecipeTag:
        """Create a new tag."""
        async with self.conn.get_cursor() as conn:
            result = await conn.fetchrow(
                load_query(__file__, CREATE_TAG_QUERY),
                tag.name,
                tag.group_id,
                tag.user_id,
            )
            if result:
                return RecipeTag(
                    id=result["id"],
                    name=tag.name,
                    group_id=tag.group_id,
                    user_id=tag.user_id,
                )
            raise RepositoryException("Failed to create tag")

    async def get_or_create_tag(self, name: str, user_id: int) -> RecipeTag:
        """Get existing tag or create new one."""
        async with self.conn.get_cursor() as conn:
            # Try to find existing tag
            result = await conn.fetchrow(
                load_query(__file__, FIND_EXISTING_TAG_QUERY),
                name,
                user_id,
            )

            if result:
                return RecipeTag(
                    id=result["id"],
                    name=result["name"],
                    group_id=result["group_id"],
                    user_id=result["user_id"],
                )

            # Create new tag
            new_tag = RecipeTag(
                id=0,  # Will be set by database
                name=name,
                group_id=None,  # Assuming no group for now
                user_id=user_id,
            )
            return await self.create_tag(new_tag)

    async def search_by_tags(self, user_id: int, tag_names: list[str]) -> list[Recipe]:
        """Search recipes by tags for a user."""
        logger.info(f"Searching recipes for user {user_id} with tags: {tag_names}")
        async with self.conn.get_cursor() as conn:
            result = await conn.fetch(
                load_query(__file__, SEARCH_RECIPES_BY_TAGS_QUERY),
                user_id,
                tag_names,
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
