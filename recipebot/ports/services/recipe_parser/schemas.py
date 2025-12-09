from pydantic import BaseModel, Field

from recipebot.domain.recipe.recipe import Ingredient


class RecipeDTO(BaseModel):
    title: str
    ingredients: list[Ingredient]
    steps: list[str]
    servings: int | None = None
    desc: str | None = Field(
        None,
        description="Short summary, could include group names, like Chicken with sauce",
    )
    time: str | None = Field("Not mentioned", description="Estimated time")
    notes: str | None = None
