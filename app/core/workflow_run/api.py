from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.core.workflow.base import Node
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
    id: int


class WorkflowRunExecuteStep(WorkflowRunExecute):
    node_id: int


class WorkflowRunExecutePublic(BaseModel):
    output_variables: list


class WorkflowRunExecuteStepPublic(BaseModel):
    output_variables: list


class NodeRun(BaseModel):
    node: Node
    output_variables: list | None = None

    @staticmethod
    def new(node: Node) -> "NodeRun":
        return NodeRun(node=node)

    def __hash__(self) -> int:
        return hash(self.node.id)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, NodeRun):
            return False
        else:
            return self.node.id == other.node.id
