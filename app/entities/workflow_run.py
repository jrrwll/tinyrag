from datetime import datetime

from sqlmodel import Field

from app.entities.base import TableBase


class WorkflowRun(TableBase, table=True):

    __tablename__ = 'workflow_run'

    workflow_id: int
    started_at: datetime | None = Field(default=None)
    stopped_at: datetime | None = Field(default=None)


class Conversation(TableBase, table=True):
    workflow_run_id: int
    node_id: int | None = Field(default=None)
    name: str = Field(max_length=255)
    summary: str = Field(max_length=1024)


class Message(TableBase, table=True):
    conversation_id: int = Field()
    query: str = Field()
    answer: str = Field()
    answer_tokens: int = Field()
    error: str = Field()
