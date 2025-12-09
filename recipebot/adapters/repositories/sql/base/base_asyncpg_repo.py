from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from logging import getLogger

import asyncpg
from asyncpg.pool import PoolConnectionProxy

from recipebot.adapters.repositories.sql.base.queries import (
    CREATE_GROUPS_TABLE,
    CREATE_RECIPE_TAGS_TABLE,
    CREATE_RECIPES_TABLE,
    CREATE_USERS_GROUPS_JUNCTION_TABLE,
    CREATE_USERS_TABLE,
)
from recipebot.adapters.repositories.sql.base.utils import load_query
from recipebot.config import settings

logger = getLogger(__name__)


class AsyncpgConnection:
    """
    Async base connection for Postgres using asyncpg connection pool.
    """

    def __init__(self) -> None:
        self._pool: asyncpg.Pool | None = None

    async def init_pool(self) -> None:
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                dsn=settings.POSTGRESQL.dsn,
                min_size=1,
                max_size=10,
            )

    async def close_pool(self) -> None:
        """Close the connection pool (call at app shutdown / lifespan)."""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    @asynccontextmanager
    async def connection(self) -> AsyncIterator[PoolConnectionProxy]:
        """
        Async context manager for getting a connection from the pool.
        """
        if self._pool is None:
            raise RuntimeError("Connection pool is not initialized")
        conn = await self._pool.acquire()
        try:
            yield conn
        finally:
            await self._pool.release(conn)

    @asynccontextmanager
    async def get_cursor(self) -> AsyncIterator[PoolConnectionProxy]:
        """
        Async context manager similar to psycopg2 RealDictCursor usage.
        Yields a connection where you can execute queries without automatic transaction management.
        """
        async with self.connection() as conn:
            try:
                yield conn
            except Exception as e:
                logger.error(f"DB ERROR: {e}")
                raise

    async def init_db(self) -> None:
        """Check that tables exist, if not create them"""
        async with self.get_cursor() as conn:
            await conn.execute(load_query(__file__, CREATE_USERS_TABLE))
            await conn.execute(load_query(__file__, CREATE_GROUPS_TABLE))
            await conn.execute(load_query(__file__, CREATE_USERS_GROUPS_JUNCTION_TABLE))

            await conn.execute(load_query(__file__, CREATE_RECIPES_TABLE))
            await conn.execute(load_query(__file__, CREATE_RECIPE_TAGS_TABLE))
