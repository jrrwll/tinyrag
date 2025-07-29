from sqlmodel import Field

from app.core.workflow.enums import WorkflowStatus
from app.entities.base import TableBase, enum_field_info


class Workflow(TableBase, table=True):
    tenant_id: int
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    status: WorkflowStatus = enum_field_info(WorkflowStatus)
    graph: str
