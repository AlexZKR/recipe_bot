from pydantic import AnyHttpUrl, BaseModel


class ResolutionResult(BaseModel):
    """Result of TikTok URL resolution."""

    description: str | None
    source_url: AnyHttpUrl
