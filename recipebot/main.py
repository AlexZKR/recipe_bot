import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.ext._application import Application

from recipebot.adapters.repositories.sql.auth.user_repo import UserAsyncpgRepo
from recipebot.adapters.repositories.sql.base.base_asyncpg_repo import AsyncpgConnection
from recipebot.config import settings
from recipebot.ports.repositories.user_repository import UserRepositoryABC

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat:
        raise Exception("Not chat in the update")
    user_repo: UserRepositoryABC = context.bot_data["user_repo"]
    if not update.effective_user:
        raise Exception("No user in the update")

    user = await user_repo.add(register_data=update.effective_user)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"You have registered!\n```{user.model_dump_json()}```",
    )


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


def main() -> None:
    app: Application = (
        ApplicationBuilder()
        .token(settings.TELEGRAM_BOT_SETTINGS.token.get_secret_value())
        .post_init(on_startup)
        .post_shutdown(on_shutdown)
        .build()
    )

    start_handler = CommandHandler("register", register)
    app.add_handler(start_handler)

    app.run_polling()


if __name__ == "__main__":
    main()
