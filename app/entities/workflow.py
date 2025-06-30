import uuid

from sqlmodel import Field

from app.entities import TableBase, TableUUidBase
from app.core.workflow.enums import NodeType, WorkflowType


class Workflow(TableBase, table=True):
    type: WorkflowType = Field(default=WorkflowType.Graph)
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)


class Node(TableUUidBase, table=True):
    type: NodeType = Field()
    name: str = Field()
    description: str | None = Field(default=None)
    front_info: str | None = Field(default=None)

    workflow_id: int = Field()
    model_id: int | None = Field(default=None)
    pass


class Edge(TableUUidBase, table=True):
    source: uuid.UUID | None = Field()
    target: uuid.UUID | None = Field()
    front_info: str | None = Field(default=None)

    workflow_id: int = Field()
    predicate: str | None = Field(default=None)



