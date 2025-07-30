from sqlmodel import Field

from app.entities.base import BizTableBase


class Workspace(BizTableBase, table=True):
    tenant_id: int
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    llm_model_config:  str | None = None
    embedding_model_config:  str | None = None
    vector_store_config:  str | None = None
