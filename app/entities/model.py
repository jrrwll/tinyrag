from sqlmodel import Field

from app.core.model.enums import ModelType
from app.entities.base import BizTableBase, enum_field_info


class Model(BizTableBase, table=True):
    tenant_id: int
    type: ModelType = enum_field_info(ModelType)
    enable: bool = True
    provider_name: str = Field(max_length=100)
    model_name: str = Field(max_length=100)
    config: str
    feature_config: str


class TenantDefaultModel(BizTableBase, table=True):

    tenant_id: int
    workspace_id: int
    model_type: ModelType = enum_field_info(ModelType)
    model_id: int | None = None
    model_name: str | None = None

    def is_unset(self) -> bool:
        return not self.model_id and not self.model_name
