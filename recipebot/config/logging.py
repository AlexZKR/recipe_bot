import logging
import sys

import orjson
import structlog
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource

from recipebot.config import settings


def serialize_for_otel(_, __, event_dict):
    """Sanitizes the event_dict for OTel using orjson."""
    return orjson.loads(
        orjson.dumps(event_dict, default=str, option=orjson.OPT_NON_STR_KEYS)
    )


def configure_logging() -> None:
    # 1. Setup OTel Provider (Reads your Render/Grafana Cloud Envs automatically)
    resource = Resource.create({"service.name": settings.APP.otel_service_name})
    logger_provider = LoggerProvider(resource=resource)
    set_logger_provider(logger_provider)

    # Add OTel Exporter (Background batching for performance)
    exporter = OTLPLogExporter(
        endpoint=settings.APP.otel_exporter_otlp_endpoint,
        headers={
            "Authorization": settings.APP.otel_exporter_otlp_headers.get_secret_value(),
        },
    )
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))

    # 2. Define the Structlog Renderer based on your Config
    if settings.APP.json_logging:
        # Convenience: specialized JSON rendering for non-string keys
        renderer = structlog.processors.JSONRenderer(
            serializer=lambda obj, **kwargs: orjson.dumps(
                obj, option=orjson.OPT_NON_STR_KEYS
            )
        )
    else:
        # Convenience: Colorful, pretty console logs for local dev
        renderer = structlog.dev.ConsoleRenderer()

    # 3. Use ProcessorFormatter to bridge Structlog convenience to Stdlib
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
        ],
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    # 4. Standard Library Handlers
    # Handler A: Stdout (The one you see in Render/Terminal console)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)

    # Handler B: OTel (The one that ships to Grafana Cloud)
    otel_handler = LoggingHandler(logger_provider=logger_provider)

    # 5. Root Logger Configuration
    root_logger = logging.getLogger()
    root_logger.addHandler(stdout_handler)
    root_logger.addHandler(otel_handler)
    root_logger.setLevel(settings.APP.logging_level)

    # 6. Structlog Configuration
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            serialize_for_otel,  # Convert UUIDs and other non-serializable types
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,  # Key bridge step
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Third-party logger silencing
    for logger_name in [
        "httpx",
        "urllib3",
        "httpcore",
        "groq._base_client",
        "telegram",
        "asyncio",
    ]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
