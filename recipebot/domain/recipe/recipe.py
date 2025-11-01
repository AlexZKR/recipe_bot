from enum import StrEnum, auto
from uuid import UUID, uuid4

from pydantic import AnyHttpUrl, BaseModel, Field


class RecipeCategory(StrEnum):
    BREAKFAST = auto()
    LUNCH = auto()
    DINNER = auto()
    DESERT = auto()
    COCKTAIL = auto()


class RecipeTag(BaseModel):
    id: int
    name: str
    group_id: int
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
    tags: list[int] = Field(default_factory=list)
