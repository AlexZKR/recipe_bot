from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import AnyHttpUrl, BaseModel, Field


class RecipeCategory(StrEnum):
    BREAKFAST = "BREAKFAST"
    LUNCH = "LUNCH"
    DINNER = "DINNER"
    DESERT = "DESERT"
    COCKTAIL = "COCKTAIL"


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


class Recipe(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    ingredients: list[Ingredient]
    steps: list[str]
    category: RecipeCategory
    servings: int | None = None
    desc: str | None = Field(
        None,
        description="Short summary, could include group names, like Chicken with sauce",
    )
    estimated_time: str | None = Field("Not mentioned", description="Estimated time")
    notes: str | None = None
    link: AnyHttpUrl | None = None

    user_id: int
    tags: list[str] = Field(default_factory=list)

    def to_md(self) -> str:
        """Format recipe as plain text for display."""
        recipe_text = f"""🍽️ {self.title}

📝 Description: {self.desc or "No description"}

🍳 Ingredients:
{self.ingredients}

👨‍🍳 Steps:
{self.steps}

📊 Category: {self.category.value}
🍽️ Servings: {self.servings or "Not specified"}
⏱️ Estimated time: {self.estimated_time or "Not specified"}"""

        if self.notes:
            recipe_text += f"\n📌 Notes: {self.notes}"

        if self.link:
            recipe_text += f"\n🔗 Link: {str(self.link)}"

        if self.tags:
            tags_str = " ".join(f"#{tag}" for tag in self.tags)
            recipe_text += f"\n🏷️ Tags: {tags_str}"

        return recipe_text
