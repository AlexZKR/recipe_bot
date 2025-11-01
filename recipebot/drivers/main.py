import logging

from telegram.ext import ApplicationBuilder
from telegram.ext._application import Application

from recipebot.config import settings
from recipebot.drivers.handlers import add_handlers
from recipebot.drivers.lifespan import on_shutdown, on_startup

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def main() -> None:
    app: Application = (
        ApplicationBuilder()
        .token(settings.TELEGRAM_BOT_SETTINGS.token.get_secret_value())
        .post_init(on_startup)
        .post_shutdown(on_shutdown)
        .build()
    )
    add_handlers(app)

    app.run_polling()


if __name__ == "__main__":
    main()
