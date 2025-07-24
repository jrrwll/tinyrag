import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.core.model.enums import ModelType
from app.entities.model import Model


class ModelPublic(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    type: ModelType
    enable: bool
    provider_name: str
    model_name: str
    config: dict # type: ignore[arg-type]

    @staticmethod
    def new(item: Model) -> "ModelPublic":
        item_dict = item.model_dump(exclude_none=True)
        if item.config:
            item_dict["config"] = json.loads(item.config)
        return ModelPublic(**item_dict)

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: Any):
        if not isinstance(other, ModelPublic):
            return False
        return self.id == other.id


class ModelCreate(BaseModel):
    type: ModelType
    provider_name: str
    model_name: str
    config: dict = Field(min_length=1) # type: ignore[type-arg]

    def to_entity(self) -> Model:
        entity_dict = self.model_dump(exclude_none=True)
        entity_dict["config"] = json.dumps(self.config)
        return Model(**entity_dict)


class ModelUpdate(BaseModel):
    id: int
    model_name: str
    config: dict = Field(min_length=1)  # type: ignore[type-arg]

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
    id: int
    enable: bool


class ModelTestRun(BaseModel):
    id: int
    prompt: str | None = None


class ModelTestRunPublic(BaseModel):
    result: dict  # type: ignore[type-arg]


class SetupDefaultModel(BaseModel):
    model_type: ModelType | None = None
    model_id: int | None = None
