"""Mock recipe tag repository for testing."""

from recipebot.domain.recipe.recipe import RecipeTag
from recipebot.ports.repositories.recipe_tag_repository import RecipeTagRepositoryABC


class MockRecipeTagRepo(RecipeTagRepositoryABC):
    """Mock implementation of recipe tag repository for testing."""

    def __init__(self):
        self._tags = []
        self._next_tag_id = 1

    async def get_user_tags(self, user_id: int) -> list[RecipeTag]:
        """Get all tags created by a user."""
        return [tag for tag in self._tags if tag.user_id == user_id]

    async def create_tag(self, tag: RecipeTag) -> RecipeTag:
        """Create a new tag."""
        new_tag = RecipeTag(
            id=self._next_tag_id,
            name=tag.name,
            group_id=tag.group_id,
            user_id=tag.user_id,
        )
        self._tags.append(new_tag)
        self._next_tag_id += 1
        return new_tag

    async def get_or_create_tag(self, name: str, user_id: int) -> RecipeTag:
        """Get existing tag or create new one."""
        # Try to find existing tag
        for tag in self._tags:
            if tag.name == name and tag.user_id == user_id:
                return tag

        # Create new tag
        new_tag = RecipeTag(
            id=0,  # Will be set by create_tag
            name=name,
            group_id=None,
            user_id=user_id,
        )
        return await self.create_tag(new_tag)

    def get_tags(self) -> list[RecipeTag]:
        """Helper method to get all tags for testing purposes."""
        return self._tags.copy()
