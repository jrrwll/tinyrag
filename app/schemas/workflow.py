from pydantic import BaseModel

from app.core.workflow.enums import WorkflowType
from app.entities.workflow import Edge, Node


class WorkflowPublic(BaseModel):
    id: int
    created_at: str
    updated_at: str

    type: WorkflowType
    name: str
    description: str | None = None

    # Dag
    nodes: list["Node"] | None
    edges: list["Edge"] | None


class WorkflowCreate(BaseModel):
    type: WorkflowType
    name: str
    description: str | None = None

    # Dag
    nodes: list["Node"] | None
    edges: list["Edge"] | None
