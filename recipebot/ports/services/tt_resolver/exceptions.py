from abc import ABC


class TTResolverError(Exception, ABC):
    """Base exception for TTResolver errors."""

    pass


class InvalidTikTokURL(TTResolverError):
    """Raised when the provided URL is not a valid TikTok URL."""

    pass


class TikTokNotAccessible(TTResolverError):
    """Raised when TikTok cannot be accessed (network errors, timeouts, etc.)."""

    pass


class DescriptionNotFound(TTResolverError):
    """Raised when the description cannot be extracted from the TikTok page."""

    pass
