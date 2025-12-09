from datetime import datetime

from pydantic import BaseModel, Field


class User(BaseModel):
    tg_id: int
    username: str
    first_name: str | None = None
    last_name: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)
