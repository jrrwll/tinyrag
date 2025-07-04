from uuid import UUID

from pydantic import BaseModel


class WorkflowR
    unPublic(BaseModel):
    id: int
    created_at: str
    updated_at: str

    workflow_id: int
    workflow_name: str

    started_at: str | None = None
    stopped_at: str | None = None
    # conversation: list["Conversation"]


class WorkflowRunCreate(BaseModel):
    workflow_id: int


class WorkflowRunStepCreate(WorkflowRunCreate):
    node_id: UUID


class NodeRun:
    pass


class EdgeRun:
    pass
