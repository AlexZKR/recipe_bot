from abc import ABC, abstractmethod

from httpx import Response

from recipebot.infra.transport.schemas import HTTPRequestData, ResponseContent


class AbstractAsyncHTTPTransport(ABC):
    @abstractmethod
    async def request(self, data: HTTPRequestData) -> ResponseContent: ...

    @abstractmethod
    async def stream(self, data: HTTPRequestData) -> Response:
        """Streaming request

        Returns:
            tuple[int, Iterator[bytes]]: content-length, iterator
        """
