import logging
from typing import cast

from recipebot.config import settings
from recipebot.config.logging.filters import TelegramContextFilter
from recipebot.config.logging.json_logging import JSONFormatter
from recipebot.config.logging.text_logging import configure_text_logging


def configure_logging() -> None:
    """Configure logging with JSON format by default for external systems.

    JSON logging is enabled by default for production monitoring.
    Set json_logging: false in config for human-readable text logs.
    """

    if settings.APP.json_logging:
        formatter = cast(logging.Formatter, JSONFormatter())
    else:
        formatter = configure_text_logging()

    context_filter = TelegramContextFilter()

    root_logger = logging.getLogger()
    root_logger.setLevel(settings.APP.logging_level)

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add console handler with formatter and filter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.addFilter(context_filter)
    root_logger.addHandler(console_handler)

    # Configure third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.INFO)
    logging.getLogger("telegram").setLevel(logging.INFO)
