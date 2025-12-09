from abc import ABC, abstractmethod

from httpx import Response

from recipebot.infra.transport.schemas import (
    HTTPRequestData,
    ResponseContent,
    ResponseMetadata,
)


class AbstractAsyncHTTPTransport(ABC):
    @abstractmethod
    async def request(
        self, data: HTTPRequestData
    ) -> tuple[ResponseContent, ResponseMetadata]: ...

    @abstractmethod
    async def stream(self, data: HTTPRequestData) -> Response:
        """Streaming request

        Returns:
            httpx.Response object
        """
