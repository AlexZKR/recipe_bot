import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.ext._application import Application

from recipebot.config import settings
from recipebot.drivers.auth.decorators.registered import only_registered
from recipebot.drivers.lifespan import on_shutdown, on_startup
from recipebot.drivers.state import get_state

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


@only_registered
async def for_registered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat:
        raise Exception("Not chat in the update")

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="You are registered in the bot!",
    )


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat:
        raise Exception("Not chat in the update")
    user_repo = get_state(context)["user_repo"]
    if not update.effective_user:
        raise Exception("No user in the update")

    user = await user_repo.add(register_data=update.effective_user)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"You have registered!\n```{user.model_dump_json()}```",
    )


def main() -> None:
    app: Application = (
        ApplicationBuilder()
        .token(settings.TELEGRAM_BOT_SETTINGS.token.get_secret_value())
        .post_init(on_startup)
        .post_shutdown(on_shutdown)
        .build()
    )

    start_handler = CommandHandler("register", register)
    registered_handler = CommandHandler("is_registered", for_registered)
    app.add_handler(start_handler)
    app.add_handler(registered_handler)

    app.run_polling()


if __name__ == "__main__":
    main()
