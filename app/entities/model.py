from sqlmodel import Field

from app.core.model.enums import ModelType
from app.entities.base import TableBase


class Model(TableBase, table=True):
    type: ModelType = Field(default=ModelType.LLM)
    enable: bool = Field(default=True)
    provider_name: str = Field(max_length=100)
    model_name: str = Field(unique=True, index=True, max_length=100)
    base_url: str | None = Field(max_length=1000)
    api_key: str | None = Field(default=None, max_length=1000)
    config: str | None = Field(default=None)


class DefaultModel(TableBase, table=True):

    __tablename__ = 'default_model'

    model_type: ModelType
    model_id: int | None = None
