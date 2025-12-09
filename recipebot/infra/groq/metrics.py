import logging
from typing import Any

from groq.types.chat import ChatCompletion
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class GroqUsageMetrics(BaseModel):
    """Metrics collected from Groq API usage."""

    model: str = Field(..., description="The model used for the API call")
    total_tokens: int = Field(
        ..., description="Total tokens used (prompt + completion)"
    )
    prompt_tokens: int = Field(..., description="Tokens used in the prompt")
    completion_tokens: int = Field(..., description="Tokens used in the completion")
    cached_tokens: int | None = Field(None, description="Tokens served from cache")
    completion_time: float = Field(..., description="Time spent generating completion")
    queue_time: float = Field(..., description="Time spent in queue")
    prompt_time: float = Field(..., description="Time spent processing prompt")
    total_time: float = Field(..., description="Total request time")

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to dictionary for easy serialization."""
        return self.model_dump()

    def log_metrics(self) -> None:
        """Log metrics using structured logging."""
        logger.info(
            "Groq API usage metrics",
            extra={
                "groq_metrics": self.to_dict(),
                **self.to_dict(),
            },
        )

    def log_summary(self) -> None:
        """Log a human-readable summary of metrics."""
        logger.info(
            f"Groq API call completed - Model: {self.model}, "
            f"Total Tokens: {self.total_tokens}, "
            f"Total Time: {self.total_time:.3f}s"
        )


def collect_metrics(response: ChatCompletion, model: str) -> GroqUsageMetrics:
    """Collect usage metrics from Groq API response."""
    usage = response.usage

    cached_tokens = None
    if usage.prompt_tokens_details and hasattr(
        usage.prompt_tokens_details, "cached_tokens"
    ):
        cached_tokens = getattr(
            usage.prompt_tokens_details.cached_tokens, "cached_tokens", None
        )

    return GroqUsageMetrics(
        total_tokens=usage.total_tokens,
        prompt_tokens=usage.prompt_tokens,
        completion_tokens=usage.completion_tokens,
        cached_tokens=cached_tokens,
        completion_time=usage.completion_time,
        queue_time=usage.queue_time,
        prompt_time=usage.prompt_time,
        total_time=usage.total_time,
        model=model,
    )
