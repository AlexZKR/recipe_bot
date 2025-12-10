from pydantic import BaseModel

from recipebot.domain.recipe.recipe import Ingredient


class IngredientsExtractionSchema(BaseModel):
    ingredients: list[Ingredient]


class StepsExtractionSchema(BaseModel):
    steps: list[str]
