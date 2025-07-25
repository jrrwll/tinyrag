from sqlmodel import Field

from app.core.model.enums import ModelType
from app.entities.base import TableBase, enum_field_info


class Model(TableBase, table=True):
    type: ModelType = enum_field_info(ModelType)
    enable: bool = True
    provider_name: str = Field(max_length=100)
    model_name: str = Field(unique=True, index=True, max_length=100)
    config: str
    embedding_config: str


class DefaultModel(TableBase, table=True):

    __tablename__ = 'default_model'

    model_type: ModelType
    model_id: int | None = None
