"""JSON logging configuration for external monitoring systems."""

import json
import logging
from datetime import UTC, datetime


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging compatible with external systems."""

    def format(self, record):
        # Create datetime from record timestamp with UTC timezone
        dt = datetime.fromtimestamp(record.created, tz=UTC)

        log_entry = {
            "timestamp": record.created,  # Unix timestamp (float: seconds.microseconds since epoch)
            "timestamp_iso": dt.isoformat(),  # ISO 8601 format: 2025-12-17T08:38:55.123456+00:00
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add raw context fields (reusable structured data)
        for attr in ["user_id", "chat_id", "username"]:
            value = getattr(record, attr, None)
            if value is not None:
                log_entry[attr] = value

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)
