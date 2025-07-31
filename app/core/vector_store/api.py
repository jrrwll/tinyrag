import json

from pydantic import BaseModel, Field

from app.config import settings
from app.core.vector_store.enums import VectorStoreType
from app.entities.vector_store import VectorStore
from app.util.codec import md5
from app.util.model import dump_and_update_dict


class VectorStorePublic(BaseModel):
    id: int
    name: str
    type: VectorStoreType
    config: dict # type: ignore[arg-type]

    @staticmethod
    def create(entity: VectorStore) -> "VectorStorePublic":
        entity_dict = entity.model_dump(exclude_none=True)
        if entity.config:
            entity_dict["config"] = json.loads(entity.config)

        return VectorStorePublic(**entity_dict)

    def footprint(self) -> str:
        return md5(f"{self.type} {json.dumps(self.config)}")

    def local_dir(self) -> str:
        return f"{settings.VECTOR_STORE_DIRECTORY}/{self.type.name}/{self.id}"


class VectorStoreCreate(BaseModel):
    name: str = Field(max_length=100)
    type: VectorStoreType
    config: dict # type: ignore[arg-type]

    def to_entity(self) -> VectorStore:
        entity_dict = self.model_dump(exclude_none=True)
        dump_and_update_dict(entity_dict, "config")
        return VectorStore(**entity_dict)


class SetupDefaultVectorStore(BaseModel):
    workspace_id: int | None = None
    vector_store_id: int | None = None
