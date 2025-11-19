from sqlmodel import Field

from app.core.vector_store.enums import VectorStoreType
from app.entities.base import BizTableBase, TableBase, \
    enum_field_info


class VectorStore(BizTableBase, table=True):
    tenant_id: int

    name: str = Field(max_length=100)
    type: VectorStoreType = enum_field_info(VectorStoreType)
    config: str


class TenantDefaultVectorStore(TableBase, table=True):

    tenant_id: int
    workspace_id: int = 0
    vector_store_id: int | None = None
