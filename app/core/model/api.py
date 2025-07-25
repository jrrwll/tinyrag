import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.core.model.enums import ModelType
from app.entities.model import Model
from app.util.json import dump_and_update_dict, load_and_update_dict


class ModelPublic(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime

    type: ModelType
    enable: bool
    provider_name: str
    model_name: str
    config: dict # type: ignore[arg-type]
    embedding_config:  dict # type: ignore[arg-type]

    @staticmethod
    def create(item: Model) -> "ModelPublic":
        item_dict = item.model_dump(exclude_none=True)
        load_and_update_dict(item_dict, "config", "embedding_config")
        return ModelPublic(**item_dict)

    # def __hash__(self) -> int:
    #     return hash(self.id)
    #
    # def __eq__(self, other: Any):
    #     if not isinstance(other, ModelPublic):
    #         return False
    #     return self.id == other.id


class ModelCreate(BaseModel):
    type: ModelType
    provider_name: str
    model_name: str
    config: dict = {} # type: ignore[type-arg]
    embedding_config: dict = {}

    def to_entity(self) -> Model:
        entity_dict = self.model_dump(exclude_none=True)
        dump_and_update_dict(entity_dict, "config", "embedding_config")
        return Model(**entity_dict)


class ModelUpdate(BaseModel):
    id: str
    model_name: str
    config: dict = {}  # type: ignore[type-arg]
    embedding_config: dict = {}

    def update_entity(self, entity: Model) -> None:
        config_dict = json.loads(entity.config)
        config_dict.update(self.config)

        update_dict = self.model_dump(exclude_none=True)
        update_dict.update(
            {
                "config": json.dumps(config_dict),
            }
        )
        entity.sqlmodel_update(update_dict)


class ModelUpdateEnablePublic(BaseModel):
    id: str
    enable: bool


class ModelTestRun(BaseModel):
    id: str
    prompt: str | None = None


class ModelTestRunPublic(BaseModel):
    result: dict  # type: ignore[type-arg]


class SetupDefaultModel(BaseModel):
    model_type: ModelType | None = None
    model_id: str | None = None
