import uuid

from sqlmodel import Field, Relationship

from app.entities.base import TableBase
from app.entities.workflow import Workflow


class WorkflowRun(TableBase, table=True):
    workflow: Workflow = Relationship()
    started_at: str | None = Field(default=None)
    stopped_at: str | None = Field(default=None)
    conversation: list["Conversation"] = Relationship()


class Conversation(TableBase, table=True):
    node_id: uuid.UUID | None = Field(default=None)
    name: str = Field(max_length=255)
    summary: str = Field(max_length=1024)
    messages: list["Message"] = Relationship(back_populates="conversation")


class Message(TableBase, table=True):
    conversation: Conversation = Relationship()
    query: str = Field()
    answer: str = Field()
    answer_tokens: int = Field()
    error: str = Field()
