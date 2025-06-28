import uuid

from sqlmodel import Field, Relationship

from app.models import TableBase, TableUUidBase
from app.models.base import Model
from app.models.enums import NodeType, WorkflowType


class Workflow(TableBase, table=True):
    type: WorkflowType = Field(default=WorkflowType.Dag)
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)

    # Dag
    nodes: list["Node"] | None = Relationship(
        back_populates="workflow", cascade_delete=True
    )
    edges: list["Edge"] | None = Relationship(
        back_populates="workflow", cascade_delete=True
    )


class Node(TableUUidBase, table=True):
    type: NodeType = Field(default=NodeType.Custom)
    name: str = Field()
    description: str | None = Field(default=None)
    front_info: str | None = Field(default=None)

    model: Model | None = Relationship()
    workflow: Workflow | None = Relationship()
    pass


class Edge(TableUUidBase, table=True):
    source: uuid.UUID = Field()
    target: uuid.UUID = Field()
    front_info: str | None = Field(default=None)
    workflow: Workflow | None = Relationship()
    pass
