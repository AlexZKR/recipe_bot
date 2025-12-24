import logging

import orjson
import structlog

from recipebot.config import settings


def configure_logging() -> None:
    """Configure logging with JSON format by default for external systems.

    JSON logging is enabled by default for production monitoring.
    Set json_logging: false in config for human-readable text logs.
    """

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
    ]
    processors = []
    logger_factory: (
        structlog.BytesLoggerFactory | structlog.WriteLoggerFactory | None
    ) = None

    if settings.APP.json_logging:
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            # seriialize non-string dict keys to JSON (user_data uses ENUMS as dict keys)
            structlog.processors.JSONRenderer(
                serializer=lambda obj, **kwargs: orjson.dumps(
                    obj, option=orjson.OPT_NON_STR_KEYS
                )
            ),
        ]
        logger_factory = structlog.BytesLoggerFactory()
    else:
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(),
        ]
        logger_factory = structlog.WriteLoggerFactory()

    structlog.configure(
        cache_logger_on_first_use=True,
        wrapper_class=structlog.make_filtering_bound_logger(settings.APP.logging_level),
        processors=processors,  # type: ignore[arg-type]
        logger_factory=logger_factory,
    )

    # Configure third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.INFO)
    logging.getLogger("telegram").setLevel(logging.INFO)
    logging.getLogger("groq._base_client").setLevel(logging.WARNING)
