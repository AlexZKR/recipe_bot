"""JSON logging configuration for external monitoring systems."""

import json
import logging
from datetime import UTC, datetime
from typing import Any


class SafeJSONEncoder(json.JSONEncoder):
    """JSON encoder that converts any complex object to string."""

    def default(self, obj):
        return str(obj)


def safe_serialize_value(value: Any) -> Any:
    """Safely serialize a value for JSON logging - convert complex objects to strings."""
    if value is None:
        return None

    # Handle basic JSON types
    if isinstance(value, int | float | str | bool):
        return value

    # Handle containers recursively
    if isinstance(value, dict):
        return {k: safe_serialize_value(v) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [safe_serialize_value(item) for item in value]

    # Convert everything else to string
    return str(value)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging compatible with external systems."""

    def format(self, record):
        try:
            # Create datetime from record timestamp with UTC timezone
            dt = datetime.fromtimestamp(record.created, tz=UTC)

            log_entry = {
                "timestamp": record.created,  # Unix timestamp (float: seconds.microseconds since epoch)
                "timestamp_iso": dt.isoformat(),  # ISO 8601 format: 2025-12-17T08:38:55.123456+00:00
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "user_id": safe_serialize_value(record.user_id),
                "username": safe_serialize_value(record.username),
                "chat_id": safe_serialize_value(record.chat_id),
                "user_data": safe_serialize_value(record.user_data),
            }

            # Add exception info if present
            if record.exc_info:
                log_entry["exception"] = self.formatException(record.exc_info)

            # Use safe encoder for final JSON serialization
            return json.dumps(log_entry, cls=SafeJSONEncoder)

        except Exception as e:
            # If JSON formatting fails completely, return a safe fallback
            fallback = {
                "timestamp": record.created,
                "level": record.levelname,
                "logger": record.name,
                "message": f"LOGGING ERROR: {record.getMessage()}",
                "error": f"JSON formatting failed: {str(e)}",
            }
            try:
                return json.dumps(fallback)
            except Exception:
                # Absolute fallback if even basic JSON fails
                return f'{{"timestamp": {record.created}, "level": "{record.levelname}", "logger": "{record.name}", "message": "LOGGING CRITICAL ERROR"}}'
