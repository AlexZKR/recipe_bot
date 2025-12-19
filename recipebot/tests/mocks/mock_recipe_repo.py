from uuid import UUID

from recipebot.adapters.repositories.sql.recipe.recipe_filters import RecipeFilters
from recipebot.domain.recipe.recipe import Recipe
from recipebot.ports.repositories.exceptions import RecipeNotFound
from recipebot.ports.repositories.recipe_repository import RecipeRepositoryABC
from recipebot.ports.repositories.recipe_tag_repository import RecipeTagRepositoryABC


class MockRecipeRepo(RecipeRepositoryABC):
    def __init__(self, tag_repo: RecipeTagRepositoryABC):
        self._recipes: list[Recipe] = []
        self.tag_repo = tag_repo
        self._next_tag_id = 1

    async def add(self, recipe_data: Recipe) -> Recipe:
        """Add a recipe and return it (simulating database insertion)."""
        # Simulate database insertion by assigning an ID if not present
        if recipe_data.id is None:
            recipe_data.id = UUID("12345678-1234-5678-9012-123456789012")

        # Create a new Recipe instance to simulate what would be returned from DB
        recipe = Recipe.model_validate(recipe_data.model_dump())
        self._recipes.append(recipe)
        return recipe

    async def get(self, id: UUID) -> Recipe:
        """Get a recipe by ID."""
        for recipe in self._recipes:
            if recipe.id == id:
                return recipe
        raise RecipeNotFound(f"Recipe with ID {id} not found")

    async def list_filtered(self, filters: RecipeFilters) -> list[Recipe]:
        """List recipes with optional filtering by tags and categories."""
        user_recipes = [
            recipe for recipe in self._recipes if recipe.user_id == filters.user_id
        ]

        # Apply tag filtering
        if filters.tag_names:
            filtered_recipes = []
            for recipe in user_recipes:
                recipe_tags = set(recipe.tags or [])
                search_tags = set(filters.tag_names)
                if recipe_tags.intersection(search_tags):
                    filtered_recipes.append(recipe)
            user_recipes = filtered_recipes

        # Apply category filtering
        if filters.category_names:
            filtered_recipes = []
            for recipe in user_recipes:
                if recipe.category.value in filters.category_names:
                    filtered_recipes.append(recipe)
            user_recipes = filtered_recipes

        return user_recipes

    async def update(self, recipe_data: Recipe) -> Recipe:
        """Update a recipe."""
        for i, recipe in enumerate(self._recipes):
            if recipe.id == recipe_data.id:
                self._recipes[i] = recipe_data
                return recipe_data
        raise RecipeNotFound(f"Recipe with ID {recipe_data.id} not found")

    async def delete(self, id, user_id: int) -> None:
        """Delete a recipe."""
        for i, recipe in enumerate(self._recipes):
            if recipe.id == id and recipe.user_id == user_id:
                self._recipes.pop(i)
                return
        raise RecipeNotFound(f"Recipe with ID {id} not found or access denied")

    def get_recipes(self) -> list[Recipe]:
        """Helper method to get all recipes for testing purposes."""
        return self._recipes.copy()
