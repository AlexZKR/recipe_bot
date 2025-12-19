"""Recipe tag repository implementation."""

import logging

from recipebot.adapters.repositories.sql.base.base_asyncpg_repo import AsyncpgConnection
from recipebot.adapters.repositories.sql.base.utils import load_query
from recipebot.adapters.repositories.sql.recipe_tag.queries import (
    CREATE_TAG_QUERY,
    FIND_EXISTING_TAG_QUERY,
    GET_USER_TAGS_QUERY,
)
from recipebot.domain.recipe.recipe import RecipeTag
from recipebot.ports.repositories.exceptions import RepositoryException
from recipebot.ports.repositories.recipe_tag_repository import RecipeTagRepositoryABC

logger = logging.getLogger(__name__)


class RecipeTagAsyncpgRepo(RecipeTagRepositoryABC):
    """Asyncpg implementation of recipe tag repository."""

    def __init__(self, conn: AsyncpgConnection) -> None:
        self.conn = conn

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
