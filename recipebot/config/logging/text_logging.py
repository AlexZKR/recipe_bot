"""Text logging configuration for human-readable development logs."""

import logging


class ContextFormatter(logging.Formatter):
    """Custom formatter that displays Telegram context in human-readable format."""

    def format(self, record: logging.LogRecord) -> str:
        # Format raw context values into display strings
        if hasattr(record, "user_id") and record.user_id is not None:
            record.formatted_user_id = f"[user_id:{record.user_id}]"
        else:
            record.formatted_user_id = ""

        if hasattr(record, "username") and record.username:
            record.formatted_username = f"[username:{record.username}]"
        else:
            record.formatted_username = ""

        if hasattr(record, "chat_id") and record.chat_id is not None:
            record.formatted_chat_id = f"[chat_id:{record.chat_id}]"
        else:
            record.formatted_chat_id = ""

        return super().format(record)


def configure_text_logging() -> logging.Formatter:
    """Configure and return text formatter for human-readable logging.

    Perfect for:
    - Development and debugging
    - Local console output
    - When you need to read logs directly
    """
    formatter = ContextFormatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s %(formatted_user_id)s%(formatted_username)s%(formatted_chat_id)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return formatter
