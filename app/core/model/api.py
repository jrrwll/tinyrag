import json
from typing import Any

from pydantic import BaseModel

from app.core.model.enums import ModelType
from app.entities.model import Model


class ModelPublic(BaseModel):
    id: int
    type: ModelType
    enable: bool
    provider_name: str
    model_name: str
    base_url: str | None = None
    api_key: str | None = None
    settings: dict | None = None  # type: ignore[type-arg]

    @staticmethod
    def new(item: Model) -> "ModelPublic":
        item_dict = item.model_dump(exclude_none=True)
        if item.settings:
            item_dict["settings"] = json.loads(item.settings)
        return ModelPublic(**item_dict)

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: Any):
        if not isinstance(other, Model):
            return False
        return self.id == other.id


class ModelCreate(BaseModel):
    type: ModelType
    provider_name: str
    model_name: str
    base_url: str | None = None
    api_key: str | None = None
    settings: dict = {}  # type: ignore[type-arg]

    def to_entity(self) -> Model:
        return Model.model_validate(
            self,
            update={
                "settings": json.dumps(self.settings),
            },
        )


class ModelUpdate(BaseModel):
    id: int
    model_name: str
    base_url: str | None = None
    api_key: str | None = None
    settings: dict  # type: ignore[type-arg]

    def update_entity(self, entity: Model) -> None:
        update_dict = self.model_dump(exclude_none=True)
        update_dict.update(
            {
                "settings": json.dumps(self.settings),
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
