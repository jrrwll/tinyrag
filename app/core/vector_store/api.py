from pydantic import BaseModel, Field

from app.core.vector_store.enums import VectorStoreType
from app.entities.vector_store import VectorStore
from app.util.json import load_and_update_dict


class VectorStorePublic(BaseModel):
    config: dict # type: ignore[arg-type]

    @staticmethod
    def create(item: VectorStore) -> "VectorStorePublic":
        item_dict = item.model_dump(exclude_none=True)
        load_and_update_dict(item_dict, "config")
        return VectorStorePublic(**item_dict)


class VectorStoreCreate(BaseModel):
    name: str = Field(max_length=100)
    type: VectorStoreType
    config: dict # type: ignore[arg-type]


class SetupDefaultVectorStore(BaseModel):
    vector_store_id: int | None = None
