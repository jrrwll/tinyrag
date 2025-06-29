from pydantic import BaseModel

from app.entities.workflow_run import Conversation


class WorkflowRunPublic(BaseModel):
    id: int
    created_at: str
    updated_at: str

    workflow_id: int
    started_at: str | None = None
    stopped_at: str | None = None
    conversation: list["Conversation"]


class WorkflowInput(BaseModel):
    workflow_id: int


class WorkflowOutput(BaseModel):
    id: int
    workflow_id: int
    started_at: str | None = None
    stopped_at: str | None = None
    conversation: list["Conversation"]
