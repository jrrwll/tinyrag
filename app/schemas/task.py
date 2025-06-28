from pydantic import BaseModel

from app.models.task import Conversation


class TaskPublic(BaseModel):
    id: int
    created_at: str
    updated_at: str

    workflow_id: int
    started_at: str | None = None
    stopped_at: str | None = None
    conversation: list["Conversation"]
