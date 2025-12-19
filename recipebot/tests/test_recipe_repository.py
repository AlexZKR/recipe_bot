"""Tests for recipe repository functionality."""

import pytest

from recipebot.adapters.repositories.sql.recipe.recipe_filters import RecipeFilters
from recipebot.domain.recipe.recipe import Recipe, RecipeCategory


class TestRecipeFilters:
    """Test RecipeFilters model."""

    def test_recipe_filters_creation(self):
        """Test creating RecipeFilters with various parameters."""
        # Test with just user_id
        filters = RecipeFilters(user_id=1)
        assert filters.user_id == 1
        assert filters.tag_names is None
        assert filters.category_names is None
        assert not filters.has_filters()

        # Test with tags
        filters = RecipeFilters(user_id=1, tag_names=["tag1", "tag2"])
        assert filters.user_id == 1
        assert filters.tag_names == ["tag1", "tag2"]
        assert filters.category_names is None
        assert filters.has_filters()

        # Test with categories
        filters = RecipeFilters(user_id=1, category_names=["BREAKFAST", "LUNCH"])
        assert filters.user_id == 1
        assert filters.tag_names is None
        assert filters.category_names == ["BREAKFAST", "LUNCH"]
        assert filters.has_filters()

        # Test with both tags and categories
        filters = RecipeFilters(
            user_id=1, tag_names=["tag1"], category_names=["DINNER"]
        )
        assert filters.user_id == 1
        assert filters.tag_names == ["tag1"]
        assert filters.category_names == ["DINNER"]
        assert filters.has_filters()


class TestMockRecipeRepoListFiltered:
    """Test the list_filtered method in MockRecipeRepo."""

    @pytest.fixture
    async def mock_repo_with_data(self, mock_recipe_repo):
        """Create a mock repo with test data."""
        # Create test recipes with different users, tags, and categories
        recipes_data = [
            # User 1 recipes
            {
                "title": "Recipe 1",
                "user_id": 1,
                "tags": ["quick", "easy"],
                "category": RecipeCategory.BREAKFAST,
                "ingredients": [],
                "steps": ["Step 1"],
            },
            {
                "title": "Recipe 2",
                "user_id": 1,
                "tags": ["healthy", "quick"],
                "category": RecipeCategory.LUNCH,
                "ingredients": [],
                "steps": ["Step 1"],
            },
            {
                "title": "Recipe 3",
                "user_id": 1,
                "tags": ["slow"],
                "category": RecipeCategory.DINNER,
                "ingredients": [],
                "steps": ["Step 1"],
            },
            # User 2 recipes
            {
                "title": "Recipe 4",
                "user_id": 2,
                "tags": ["quick"],
                "category": RecipeCategory.BREAKFAST,
                "ingredients": [],
                "steps": ["Step 1"],
            },
        ]

        for recipe_data in recipes_data:
            recipe = Recipe(**recipe_data)
            await mock_recipe_repo.add(recipe)

        return mock_recipe_repo

    @pytest.mark.asyncio
    async def test_list_filtered_no_filters(self, mock_repo_with_data):
        """Test list_filtered with no filters (should return all user recipes)."""
        filters = RecipeFilters(user_id=1)
        recipes = await mock_repo_with_data.list_filtered(filters)

        assert len(recipes) == 3  # noqa: PLR2004
        assert all(recipe.user_id == 1 for recipe in recipes)
        titles = {recipe.title for recipe in recipes}
        assert titles == {"Recipe 1", "Recipe 2", "Recipe 3"}

    @pytest.mark.asyncio
    async def test_list_filtered_by_tags(self, mock_repo_with_data):
        """Test list_filtered with tag filtering."""
        # Filter by single tag
        filters = RecipeFilters(user_id=1, tag_names=["quick"])
        recipes = await mock_repo_with_data.list_filtered(filters)

        assert len(recipes) == 2  # noqa: PLR2004 # Recipe 1 and Recipe 2 have "quick" tag
        titles = {recipe.title for recipe in recipes}
        assert titles == {"Recipe 1", "Recipe 2"}

        # Filter by tag that doesn't exist
        filters = RecipeFilters(user_id=1, tag_names=["nonexistent"])
        recipes = await mock_repo_with_data.list_filtered(filters)
        assert len(recipes) == 0

        # Filter by multiple tags (OR logic)
        filters = RecipeFilters(user_id=1, tag_names=["easy", "healthy"])
        recipes = await mock_repo_with_data.list_filtered(filters)
        assert len(recipes) == 2  # noqa: PLR2004 # Recipe 1 (easy) and Recipe 2 (healthy)

    @pytest.mark.asyncio
    async def test_list_filtered_by_categories(self, mock_repo_with_data):
        """Test list_filtered with category filtering."""
        # Filter by single category
        filters = RecipeFilters(user_id=1, category_names=["BREAKFAST"])
        recipes = await mock_repo_with_data.list_filtered(filters)

        assert len(recipes) == 1
        assert recipes[0].title == "Recipe 1"
        assert recipes[0].category == RecipeCategory.BREAKFAST

        # Filter by multiple categories
        filters = RecipeFilters(user_id=1, category_names=["BREAKFAST", "LUNCH"])
        recipes = await mock_repo_with_data.list_filtered(filters)

        assert len(recipes) == 2  # noqa: PLR2004
        titles = {recipe.title for recipe in recipes}
        assert titles == {"Recipe 1", "Recipe 2"}

    @pytest.mark.asyncio
    async def test_list_filtered_by_tags_and_categories(self, mock_repo_with_data):
        """Test list_filtered with both tag and category filtering."""
        # Filter by tag AND category
        filters = RecipeFilters(
            user_id=1, tag_names=["quick"], category_names=["BREAKFAST"]
        )
        recipes = await mock_repo_with_data.list_filtered(filters)

        assert len(recipes) == 1
        assert (
            recipes[0].title == "Recipe 1"
        )  # Only recipe with quick tag AND breakfast category

    @pytest.mark.asyncio
    async def test_list_filtered_different_users(self, mock_repo_with_data):
        """Test list_filtered respects user isolation."""
        # User 1 should only see their recipes
        filters = RecipeFilters(user_id=1)
        recipes = await mock_repo_with_data.list_filtered(filters)
        assert len(recipes) == 3  # noqa: PLR2004
        assert all(recipe.user_id == 1 for recipe in recipes)

        # User 2 should only see their recipes
        filters = RecipeFilters(user_id=2)
        recipes = await mock_repo_with_data.list_filtered(filters)
        assert len(recipes) == 1
        assert recipes[0].user_id == 2  # noqa: PLR2004
        assert recipes[0].title == "Recipe 4"

    @pytest.mark.asyncio
    async def test_list_filtered_empty_results(self, mock_repo_with_data):
        """Test list_filtered returns empty list when no matches."""
        # Non-existent user
        filters = RecipeFilters(user_id=999)
        recipes = await mock_repo_with_data.list_filtered(filters)
        assert len(recipes) == 0

        # User exists but no matching filters
        filters = RecipeFilters(
            user_id=1, tag_names=["nonexistent"], category_names=["NONEXISTENT"]
        )
        recipes = await mock_repo_with_data.list_filtered(filters)
        assert len(recipes) == 0
