import json
import re
from http import HTTPMethod
from urllib.parse import urlparse

from bs4 import BeautifulSoup, Tag

from recipebot.infra.transport.base import AbstractAsyncHTTPTransport
from recipebot.infra.transport.schemas import HTTPRequestData
from recipebot.ports.services.tt_resolver import ResolutionResult, TTResolverABC
from recipebot.ports.services.tt_resolver.exceptions import (
    DescriptionNotFound,
    InvalidTikTokURL,
    TikTokNotAccessible,
)


class HttpxTTResolver(TTResolverABC):
    def __init__(self, transport: AbstractAsyncHTTPTransport):
        self.transport = transport

    def _validate_tiktok_url(self, url: str) -> None:
        """Validate that the URL is a valid TikTok URL."""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise InvalidTikTokURL(f"Invalid URL format: {url}")

            # Check if it's a TikTok domain
            if not re.match(r"(?:www\.)?tiktok\.com|vm\.tiktok\.com", parsed.netloc):
                raise InvalidTikTokURL(f"Not a TikTok URL: {url}")

        except Exception as e:
            if isinstance(e, InvalidTikTokURL):
                raise
            raise InvalidTikTokURL(f"Invalid URL: {url} - {str(e)}")

    async def resolve(self, url: str) -> ResolutionResult:
        # Validate URL first
        self._validate_tiktok_url(url)

        try:
            data = HTTPRequestData(url=url, method=HTTPMethod.GET)
            html, metadata = await self.transport.request(data)
        except Exception as e:
            raise TikTokNotAccessible(f"Failed to access TikTok URL {url}: {str(e)}")

        # Extract description from HTML
        if isinstance(html, str):
            description = self._extract_description(html)
            return ResolutionResult(
                description=description, source_url=metadata.final_url
            )
        else:
            raise TikTokNotAccessible(
                f"Unexpected response type from TikTok: {type(html)}"
            )

    def _extract_description(self, html: str) -> str:
        try:
            soup = BeautifulSoup(html, "html.parser")
            script_tag = soup.find("script", id="__UNIVERSAL_DATA_FOR_REHYDRATION__")

            if not script_tag or not isinstance(script_tag, Tag):
                raise DescriptionNotFound("TikTok data script tag not found in page")

            script_content = script_tag.string
            if not script_content or not isinstance(script_content, str):
                raise DescriptionNotFound("TikTok data script tag has no content")

            try:
                data = json.loads(script_content)
            except json.JSONDecodeError as e:
                raise DescriptionNotFound(
                    f"Invalid JSON in TikTok data script: {str(e)}"
                )

            default_scope = data.get("__DEFAULT_SCOPE__", {})
            if not default_scope:
                raise DescriptionNotFound("No default scope found in TikTok data")

            item_struct = (
                default_scope.get("webapp.video-detail", {})
                .get("itemInfo", {})
                .get("itemStruct", {})
            )
            if not item_struct:
                raise DescriptionNotFound("Video details not found in TikTok data")

            desc = item_struct.get("desc")
            if not desc:
                raise DescriptionNotFound("No description found in video details")

            return desc

        except DescriptionNotFound:
            raise
        except Exception as e:
            raise DescriptionNotFound(
                f"Failed to extract description from TikTok page: {str(e)}"
            )
