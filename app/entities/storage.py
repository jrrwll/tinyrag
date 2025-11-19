from sqlmodel import Field

from app.core.storage.enums import StorageType
from app.entities.base import BizTableBase, TableBase, \
    enum_field_info


class Storage(BizTableBase, table=True):
    id: int = Field(primary_key=True)
    tenant_id: int

    name: str = Field(max_length=100)
    type: StorageType = enum_field_info(StorageType)
    config: str


class TenantDefaultStorage(TableBase, table=True):

    tenant_id: int
    workspace_id: int = 0
    storage_id: int | None = None
