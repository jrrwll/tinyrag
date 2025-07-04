from datetime import datetime

from pydantic import BaseModel

from app.entities.workflow import Workflow
from app.entities.workflow_run import WorkflowRun


class WorkflowRunPublic(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    workflow_id: int
    workflow_name: str

    started_at: datetime | None = None
    stopped_at: datetime | None = None
    # conversation: list["Conversation"]

    @staticmethod
    def new(entity: WorkflowRun, workflow_entity: Workflow) -> "WorkflowRunPublic":
        return WorkflowRunPublic(
            workflow_name=workflow_entity.name,
            **entity.model_dump()
        )


class WorkflowRunCreate(BaseModel):
    workflow_id: int

    def to_entity(self) -> WorkflowRun:
        return WorkflowRun(**self.model_dump())


class WorkflowRunExecute(BaseModel):
    workflow_run_id: int


class WorkflowRunExecuteStep(WorkflowRunExecute):
    node_id: int


class WorkflowRunExecutePublic(BaseModel):
    pass


class WorkflowRunExecuteStepPublic(BaseModel):
    pass


class NodeRun:
    pass


class EdgeRun:
    pass
