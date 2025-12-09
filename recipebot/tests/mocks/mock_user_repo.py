from datetime import datetime

from telegram import User as TGUser

from recipebot.domain.auth.user import User
from recipebot.ports.repositories.user_repository import UserRepositoryABC


class MockUserRepo(UserRepositoryABC):
    def __init__(self):
        self._users = []

    async def add(self, register_data: TGUser) -> User:
        user = User(
            tg_id=register_data.id,
            username=register_data.username or "",
            first_name=register_data.first_name,
            last_name=register_data.last_name,
            created_at=datetime.now(),
        )
        self._users.append(user)
        return user

    async def get(self, id: int) -> User | None:
        for user in self._users:
            if user.tg_id == id:
                return user
        return None

    async def get_by_tg_user(self, user: TGUser | None) -> User | None:
        if not user:
            return None
        return await self.get(user.id)
