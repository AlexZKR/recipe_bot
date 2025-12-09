from enum import StrEnum
from http import HTTPMethod
from typing import Any

from pydantic import BaseModel

ResponseContent = dict[str, Any] | str


class ResponseMetadata(BaseModel):
    """Metadata from HTTP response."""

    final_url: str
    status_code: int
    headers: dict[str, Any]
    content_type: str | None = None
    redirect_chain: list[str] | None = None


class ContentTypeEnum(StrEnum):
    binary_octet_stream = "binary/octet-stream"
    json = "application/json"
    text_html = "text/html"


class HTTPRequestData(BaseModel):
    method: HTTPMethod
    url: str
    params: dict[str, Any] | None = None
    headers: dict[str, Any] | None = None
