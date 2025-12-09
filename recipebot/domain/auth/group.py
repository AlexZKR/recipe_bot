from pydantic import BaseModel, Field


class Group(BaseModel):
    tg_chat_id: int
    name: str
    member_ids: list[int] = Field(default_factory=list)
