from abc import ABC, abstractmethod

from telegram import User as TGUser

from recipebot.domain.auth.user import User


class UserRepositoryABC(ABC):
    @abstractmethod
    async def add(self, register_data: TGUser) -> User:
        pass

    @abstractmethod
    async def get_by_tg_id(self, id: int) -> User | None:
        pass
