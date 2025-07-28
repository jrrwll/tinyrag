from sqlmodel import Field

from app.core.model.enums import ModelType
from app.entities.base import TableBase, enum_field_info


class Model(TableBase, table=True):
    type: ModelType = enum_field_info(ModelType)
    enable: bool = True
    workspace_id: int
    provider_name: str = Field(max_length=100)
    model_name: str = Field(unique=True, index=True, max_length=100)
    config: str
