import logging
from threading import Thread

from telegram.ext import ApplicationBuilder, PicklePersistence
from telegram.ext._application import Application

from recipebot.config import settings
from recipebot.config.logging import configure_logging
from recipebot.drivers.handlers import add_handlers
from recipebot.drivers.lifespan import on_shutdown, on_startup
from recipebot.drivers.metrics_server import start_metrics_server

logger = logging.getLogger(__name__)


def main() -> None:
    configure_logging()
    metrics_thread = Thread(target=start_metrics_server, daemon=True)
    metrics_thread.start()

    persistence = PicklePersistence(filepath="recipebot.pickle")
    app: Application = (
        ApplicationBuilder()
        .token(settings.TELEGRAM_BOT_SETTINGS.token.get_secret_value())
        .persistence(persistence)
        .post_init(on_startup)
        .post_shutdown(on_shutdown)
        .build()
    )
    add_handlers(app)

    app.run_polling()


if __name__ == "__main__":
    main()
