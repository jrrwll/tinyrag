from sqlmodel import Field

from app.core.workflow.enums import WorkflowStatus, WorkflowType
from app.entities.base import TableBase


class Workflow(TableBase, table=True):
    type: WorkflowType = Field(default=WorkflowType.Graph)
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    status: WorkflowStatus = Field(default=WorkflowStatus.Draft)

    graph: str | None = Field(default=None)
