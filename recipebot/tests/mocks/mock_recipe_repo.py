from uuid import UUID

from recipebot.domain.recipe.recipe import Recipe
from recipebot.ports.repositories.exceptions import RecipeNotFound
from recipebot.ports.repositories.recipe_repository import RecipeRepositoryABC


class MockRecipeRepo(RecipeRepositoryABC):
    def __init__(self):
        self._recipes = []

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

    async def list_by_user(self, user_id: int) -> list[Recipe]:
        """List all recipes for a user."""
        return [recipe for recipe in self._recipes if recipe.user_id == user_id]

    async def update(self, recipe_data: Recipe) -> Recipe:
        """Update a recipe."""
        for i, recipe in enumerate(self._recipes):
            if recipe.id == recipe_data.id:
                self._recipes[i] = recipe_data
                return recipe_data
        raise ValueError(f"Recipe with ID {recipe_data.id} not found")

    def get_recipes(self) -> list[Recipe]:
        """Helper method to get all recipes for testing purposes."""
        return self._recipes.copy()
