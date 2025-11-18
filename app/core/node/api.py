from pydantic import BaseModel

from app.core.workflow.enums import NodeType


class NodePublic(BaseModel):
    id: int
    type: NodeType
    config: dict # type: ignore[type-arg]

