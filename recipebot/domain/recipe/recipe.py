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


class Recipe(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    ingredients: str
    steps: str
    category: RecipeCategory
    servings: int | None = None
    description: str | None = None
    estimated_time: str | None = None
    notes: str | None = None
    link: AnyHttpUrl | None = None

    user_id: int
    tags: list[str] = Field(default_factory=list)

    def to_md(self) -> str:
        """Format recipe as plain text for display."""
        recipe_text = f"""🍽️ {self.title}

📝 Description: {self.description or "No description"}

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
