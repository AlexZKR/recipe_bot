from uuid import UUID


class RepositoryException(Exception): ...


class UserNotFound(RepositoryException): ...


class UserAlreadyExists(RepositoryException): ...


class RecipeNotFound(RepositoryException):
    def __init__(
        self, message: str = "Recipe not found", recipe_id: UUID | None = None
    ) -> None:
        self.message = message
        self.recipe_id = recipe_id
        super().__init__(self.message, self.recipe_id)
