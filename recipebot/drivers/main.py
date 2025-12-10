import logging
from threading import Thread

from telegram.ext import ApplicationBuilder, PicklePersistence
from telegram.ext._application import Application

from recipebot.config import settings
from recipebot.config.enums import AppEnvironment
from recipebot.drivers.handlers import add_handlers
from recipebot.drivers.keepalive import start_health_check
from recipebot.drivers.lifespan import on_shutdown, on_startup

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


def main() -> None:
    health_thread = Thread(target=start_health_check, daemon=True)
    health_thread.start()

    persistence = PicklePersistence(filepath="recipebot.pickle")
    token = (
        settings.TELEGRAM_BOT_SETTINGS.test_token.get_secret_value()
        if settings.APP.env == AppEnvironment.DEV
        else settings.TELEGRAM_BOT_SETTINGS.prod_token.get_secret_value()
    )
    app: Application = (
        ApplicationBuilder()
        .token(token)
        .persistence(persistence)
        .post_init(on_startup)
        .post_shutdown(on_shutdown)
        .build()
    )
    add_handlers(app)

    app.run_polling()


if __name__ == "__main__":
    main()
