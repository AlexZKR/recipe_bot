from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    tg_id: int
    username: str
    first_name: str | None = None
    last_name: str | None = None
    created_at: datetime
