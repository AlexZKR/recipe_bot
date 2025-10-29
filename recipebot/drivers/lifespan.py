from logging import getLogger

from telegram.ext._application import Application

from recipebot.adapters.repositories.sql.auth.user_repo.user_repo import UserAsyncpgRepo
from recipebot.adapters.repositories.sql.base.base_asyncpg_repo import AsyncpgConnection

logger = getLogger(__name__)


async def on_startup(app: Application):
    logger.info("Bot startup: initializing DB connection pool")
    asyncpg_conn = AsyncpgConnection()
    await asyncpg_conn.init_pool()
    await asyncpg_conn.init_db()

    user_repo = UserAsyncpgRepo(asyncpg_conn)
    app.bot_data["user_repo"] = user_repo
    app.bot_data["asyncpg_conn"] = asyncpg_conn


async def on_shutdown(app: Application):
    logger.info("Bot shutdown: closing DB connection pool")
    asyncpg_conn: AsyncpgConnection = app.bot_data.get("asyncpg_conn")
    if asyncpg_conn:
        await asyncpg_conn.close_pool()
