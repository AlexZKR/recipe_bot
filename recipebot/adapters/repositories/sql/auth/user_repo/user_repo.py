from logging import getLogger

from telegram import User as TGUser

from recipebot.adapters.repositories.sql.auth.user_repo.queries import (
    GET_BY_TG_ID_QUERY,
    INSERT_USER_QUERY,
)
from recipebot.adapters.repositories.sql.base.base_asyncpg_repo import (
    AsyncpgConnection,
)
from recipebot.adapters.repositories.sql.base.utils import load_query
from recipebot.domain.auth.user import User
from recipebot.ports.repositories.exceptions import UserAlreadyExists, UserNotFound
from recipebot.ports.repositories.user_repository import UserRepositoryABC

logger = getLogger(__name__)


class UserAsyncpgRepo(UserRepositoryABC):
    def __init__(self, conn: AsyncpgConnection) -> None:
        self.conn = conn

    async def add(self, register_data: TGUser) -> User:
        logger.info("Starting user registration")
        async with self.conn.get_cursor() as conn:
            if await self.get(register_data.id):
                raise UserAlreadyExists(
                    f"Username {register_data.username} already registered."
                )

            row = await conn.fetchrow(
                load_query(__file__, INSERT_USER_QUERY),
                register_data.id,
                register_data.username,
                register_data.first_name,
                register_data.last_name,
            )
            if not row:
                raise Exception("User not created")

            return User.model_validate(dict(row))

    async def get(self, id: int) -> User | None:
        async with self.conn.get_cursor() as conn:
            row = await conn.fetchrow(load_query(__file__, GET_BY_TG_ID_QUERY), id)
            if not row:
                return None
            return User(**dict(row))

    async def get_by_tg_user(self, user: TGUser | None) -> User | None:
        if not user:
            raise UserNotFound("TG user wasn't provided")
        return await self.get(user.id)
