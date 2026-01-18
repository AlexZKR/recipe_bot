from collections import defaultdict
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import AnyHttpUrl, BaseModel, Field


class RecipeCategory(StrEnum):
    BREAKFAST = "BREAKFAST"  # Covers breakfast and brunch
    MAIN_COURSE = "MAIN_COURSE"  # The united Lunch/Dinner category
    SALAD = "SALAD"  # Salads (could be sides or mains)
    SOUP = "SOUP"  # Soups, stews, and broths
    SNACK = "SNACK"  # Appetizers, finger foods, small bites
    DESSERT = "DESSERT"  # Fixed spelling (Sweets, cakes, cookies)
    DRINK = "DRINK"  # Broader than COCKTAIL (includes smoothies, coffee, etc.)
    SAUCE = "SAUCE"  # Sauces, dressings, marinades, dips


class RecipeTag(BaseModel):
    id: int
    name: str
    group_id: int | None = None
    user_id: int


class Ingredient(BaseModel):
    name: str
    qty: str | None = Field(None, description="Quantity as string")
    unit: str | None = None
    group: str = Field(
        "Main",
        description="The section this ingredient belongs to (e.g., 'Sauce', 'Marinade', 'Dough'). Translate to English.",
    )

    def basic_info(self) -> str:
        # Build a list of parts that exist (not None)
        parts = [p for p in [self.qty, self.unit, self.name] if p]

        # Join them with spaces (e.g., "3 tbsp flour" instead of "3tbspflour")
        return " ".join(parts)


class RecipeDTO(BaseModel):
    title: str
    ingredients: list[Ingredient]
    steps: list[str]
    servings: int | None = None
    desc: str | None = Field(
        None,
        description="Short summary, could include group names, like Chicken with sauce",
    )
    estimated_time: str | None = Field("Not mentioned", description="Estimated time")
    notes: str | None = None
    link: AnyHttpUrl | None = None

    def to_md(self) -> str:
        """Format recipe as plain text for display."""
        recipe_text = f"""🍽️ {self.title}

📝 Description: {self.desc or "No description"}

🍳 Ingredients:
"""

        # Format ingredients nicely, grouped by category
        if self.ingredients:
            # Group ingredients by their group field
            grouped_ingredients = defaultdict(list)

            for ingredient in self.ingredients:
                grouped_ingredients[ingredient.group].append(ingredient)

            # Display each group
            for group_name, ingredients_in_group in grouped_ingredients.items():
                recipe_text += f"\n**{group_name}:**\n"
                for ingredient in ingredients_in_group:
                    recipe_text += f"• {ingredient.basic_info()}\n"
        else:
            recipe_text += "No ingredients specified\n"

        recipe_text += """
👨‍🍳 Steps:
"""

        # Format steps as numbered list
        if self.steps:
            for i, step in enumerate(self.steps, 1):
                recipe_text += f"{i}. {step}\n"
        else:
            recipe_text += "No steps specified\n"

        recipe_text += f"""
🍽️ Servings: {self.servings or "Not specified"}
⏱️ Estimated time: {self.estimated_time or "Not specified"}"""

        if self.notes:
            recipe_text += f"\n📌 Notes: {self.notes}"

        if self.link:
            recipe_text += f"\n🔗 Link: {str(self.link)}"

        return recipe_text


class Recipe(RecipeDTO):
    id: UUID = Field(default_factory=uuid4)
    category: RecipeCategory

    user_id: int
    tags: list[str] = Field(default_factory=list)

    def to_md(self) -> str:
        """Format recipe as plain text for display."""
        # Start with the basic recipe info from parent
        recipe_text = super().to_md()

        # Add category info
        recipe_text += f"\n📊 Category: {self.category.value}"

        # Add tags if present
        if self.tags:
            tags_str = " ".join(f"#{tag}" for tag in self.tags)
            recipe_text += f"\n🏷️ Tags: {tags_str}"

        return recipe_text
