import json
from datetime import datetime
from pydantic import BaseModel, Field

from app.config import settings
from app.core.storage.enums import StorageType
from app.entities.storage import Storage
from app.util.codec import md5
from app.util.model import dump_and_update_dict, load_and_update_dict


class StorageSimplePublic(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    name: str
    type: StorageType


class StoragePublic(StorageSimplePublic):
    config: dict # type: ignore[arg-type]

    @staticmethod
    def create(entity: Storage) -> "StoragePublic":
        entity_dict = entity.model_dump(exclude_none=True)
        load_and_update_dict(entity_dict, "config")
        return StoragePublic(**entity_dict)

    def footprint(self) -> str:
        return md5(f"{json.dumps(self.config)}")

    def local_dir(self) -> str:
        return f"{settings.STORAGE_DIRECTORY}/{self.type.name}/{self.id}"


class StorageCreate(BaseModel):
    name: str = Field(max_length=100)
    type: StorageType
    config: dict # type: ignore[arg-type]

    def to_entity(self) -> Storage:
        entity_dict = self.model_dump(exclude_none=True)
        dump_and_update_dict(entity_dict, "config")
        return Storage(**entity_dict)


class StorageUpdateConfig(BaseModel):
    id: int
    config: dict  # type: ignore[type-arg]

    def update_entity(self, entity: Storage) -> None:
        update_dict = self.model_dump(exclude={"id"})
        dump_and_update_dict(update_dict, "config")
        entity.sqlmodel_update(update_dict)


class StorageUpdate(BaseModel):
    id: int
    name: str = Field(max_length=100)

    def update_entity(self, entity: Storage) -> None:
        update_dict = self.model_dump(exclude={"id"}, exclude_none=True)
        entity.sqlmodel_update(update_dict)


class SetupDefaultStorage(BaseModel):
    workspace_id: int | None = None
    storage_id: int | None = None
