from pydantic import BaseModel


class ClassifyVariable(BaseModel):
    name: str
    node_id: int | None = None


class ClassifyTopic(BaseModel):
    value: str
    topic: str | None = None
    other_topic: bool | None = None
    node_id: int | None = None
