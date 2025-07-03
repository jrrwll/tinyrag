import json
from datetime import datetime

from pydantic import BaseModel

from app.core.workflow.base import WorkflowGraph
from app.core.workflow.enums import WorkflowStatus, WorkflowType
from app.entities.workflow import Workflow


class WorkflowCreate(BaseModel):
    type: WorkflowType
    name: str
    description: str | None = None

    # graph
    graph: WorkflowGraph | None = None

    def to_entity(self) -> Workflow:
        update_dict = {}
        if self.graph:
            update_dict["graph"] = self.graph.model_dump_json()
        return Workflow.model_validate(self, update=update_dict)


class WorkflowUpdate(WorkflowCreate):
    id: int

    def update_entity(self, entity: Workflow) -> None:
        update_dict = self.model_dump(exclude_none=True)
        if self.graph:
            update_dict.update(
                {
                    "graph": self.graph.model_dump_json(),
                }
            )
        entity.sqlmodel_update(update_dict)


class WorkflowPublic(WorkflowCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    status: WorkflowStatus

    @staticmethod
    def new(item: Workflow) -> "WorkflowPublic":
        item_dict = item.model_dump(exclude_none=True)
        if item.graph:
            item_dict["graph"] = json.loads(item.graph)
        return WorkflowPublic(**item_dict)
