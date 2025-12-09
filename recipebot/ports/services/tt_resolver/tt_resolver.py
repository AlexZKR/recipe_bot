from abc import ABC, abstractmethod


class TTResolverABC(ABC):
    """Resolve TikTok recipe description from URL."""

    @abstractmethod
    async def resolve(self, url: str) -> str:
        """Resolve TikTok description from URL.

        Args:
            url: TikTok video URL

        Raises:
            InvalidTikTokURL: If the URL is not a valid TikTok URL
            TikTokNotAccessible: If the TikTok page cannot be accessed
            DescriptionNotFound: If the description cannot be extracted

        Returns:
            The video description text
        """
        pass
