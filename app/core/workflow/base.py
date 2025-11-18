from typing import Any

from pydantic import BaseModel

from app.core.workflow.enums import NodeType


class WorkflowGraph(BaseModel):
    nodes: list["Node"]
    edges: list["Edge"]

    front_info: str | None = None


class Node(BaseModel):
    id: int
    name: str
    description: str | None = None
    type: NodeType

    config: dict # type: ignore[type-arg]
    front_info: str | None = None

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Node):
            return False
        else:
            return self.id == other.id


class Edge(BaseModel):
    source: int
    target: int

    front_info: str | None = None

    def __hash__(self) -> int:
        return hash((self.source, self.target))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Edge):
            return False
        else:
            return self.source == other.source and self.target == other.target
