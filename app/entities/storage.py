from sqlmodel import Field

from app.core.storage.enums import StorageType
from app.entities.base import TableBase, \
    enum_field_info


class Storage(TableBase, table=True):
    id: int = Field(primary_key=True)
    tenant_id: int

    name: str = Field(max_length=100)
    type: StorageType = enum_field_info(StorageType)
    config: str


class TenantDefaultStorage(TableBase, table=True):

    tenant_id: int
    workspace_id: int
    storage_id: int | None = None

    def is_unset(self) -> bool:
        return not self.storage_id
