from datetime import datetime

from sqlmodel import Field

from app.entities.base import TableBase


class WorkflowRun(TableBase, table=True):

    workflow_id: int
    started_at: datetime | None = None
    stopped_at: datetime | None = None


class WorkflowConversation(TableBase, table=True):
    workflow_run_id: int
    node_id: int | None = None
    name: str = Field(max_length=255)
    summary: str = Field(max_length=1024)


class WorkflowMessage(TableBase, table=True):
    conversation_id: int
    query: str = Field()
    answer: str = Field()
    answer_tokens: int = Field()
    error: str = Field()
