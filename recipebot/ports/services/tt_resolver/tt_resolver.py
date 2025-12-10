from abc import ABC, abstractmethod

from pydantic import BaseModel


class ResolutionResult(BaseModel):
    """Result of TikTok URL resolution."""

    description: str | None
    source_url: str


class TTResolverABC(ABC):
    """Resolve TikTok recipe description from URL."""

    @abstractmethod
    async def resolve(self, url: str) -> ResolutionResult:
        """Resolve TikTok description from URL.

        Args:
            url: TikTok video URL

        Raises:
            InvalidTikTokURL: If the URL is not a valid TikTok URL
            TikTokNotAccessible: If the TikTok page cannot be accessed
            DescriptionNotFound: If the description cannot be extracted

        Returns:
            ResolutionResult with description and source URL
        """
        pass
