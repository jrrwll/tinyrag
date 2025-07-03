from uuid import UUID

from pydantic import BaseModel

from app.core.workflow.enums import WorkflowType


class WorkflowRunPublic(BaseModel):
    id: int
    created_at: str
    updated_at: str

    workflow_id: int
    workflow_name: str
    workflow_type: WorkflowType

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
