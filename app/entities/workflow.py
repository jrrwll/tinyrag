from sqlmodel import Field

from app.core.workflow.enums import WorkflowStatus
from app.entities.base import TableBase


class Workflow(TableBase, table=True):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    status: WorkflowStatus
    graph: str
