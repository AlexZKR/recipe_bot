import json
from collections.abc import Iterable
from typing import TypeVar

from groq import AsyncGroq
from groq.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

from recipebot.config.config import GroqSettings
from recipebot.infra.groq.metrics import collect_metrics

T = TypeVar("T", bound=BaseModel)


class GroqClient:
    def __init__(self, settings: GroqSettings):
        self.client = AsyncGroq(api_key=settings.api_key.get_secret_value())

    async def get_json_structured_output_completion(
        self,
        model: str,
        messages: Iterable[ChatCompletionMessageParam],
        schema: type[T],
        schema_name: str,
    ) -> T:
        """Get structured output completion with usage metrics.

        Returns:
            Parsed response
        """
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": schema_name,
                    "schema": schema.model_json_schema(),
                },
            },
            temperature=0,
        )
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("Received empty response from Groq API")

        # TODO: Log metrics to database
        collect_metrics(response, model).log_metrics()

        parsed_response = schema.model_validate(json.loads(content))
        return parsed_response
