import json
from datetime import datetime
from functools import cache
from typing import Self

from pydantic import BaseModel, Field, model_validator

from app.common.constants import MIN_UTC_DATETIME
from app.core.model.base import ModelFeatureConfig
from app.core.model.builtin_models import get_builtin_model
from app.core.model.enums import BUILTIN_MODEL_PROVIDER_NAME, ModelType
from app.entities.model import Model
from app.util.codec import md5
from app.util.model import dump_and_update_dict, load_and_update_dict


class ModelSimplePublic(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    name: str
    type: ModelType
    model_name: str
    provider_name: str
    enable: bool


class ModelPublic(ModelSimplePublic):
    config: dict  # type: ignore[arg-type]
    feature_config: ModelFeatureConfig

    @staticmethod
    def create(entity: Model) -> "ModelPublic":
        entity_dict = entity.model_dump(exclude_none=True)
        load_and_update_dict(entity_dict, "config",
                             feature_config=ModelFeatureConfig)
        return ModelPublic.model_construct(**entity_dict)

    @staticmethod
    @cache
    def from_builtin(model_type: ModelType, model_name: str) -> "ModelPublic":
        model = get_builtin_model(model_type, model_name)
        model_config = model.model_dump()
        return ModelPublic(
            id=model.id,
            created_at=MIN_UTC_DATETIME,
            updated_at=MIN_UTC_DATETIME,
            name=model_name,
            type=model_type,
            enable=True,
            provider_name=BUILTIN_MODEL_PROVIDER_NAME,
            model_name=model_name,
            config=model_config,
            feature_config=model_config,
        )

    def is_builtin(self) -> bool:
        return self.provider_name == BUILTIN_MODEL_PROVIDER_NAME

    def footprint(self) -> str:
        return md5(f"{self.provider_name} {self.model_name} "
                   f"{json.dumps(self.config)}")

    # def __hash__(self) -> int:
    #     return hash(self.id)
    #
    # def __eq__(self, other: Any):
    #     if not isinstance(other, ModelPublic):
    #         return False
    #     return self.id == other.id


class ModelCreate(BaseModel):
    name: str = Field(max_length=100)
    type: ModelType
    provider_name: str
    model_name: str
    config: dict = {}  # type: ignore[type-arg]

    def to_entity(self) -> Model:
        entity_dict = self.model_dump(exclude_none=True)
        dump_and_update_dict(entity_dict, "config")
        return Model(**entity_dict)


class ModelUpdateConfig(BaseModel):
    id: int
    config: dict  # type: ignore[type-arg]

    def update_entity(self, entity: Model) -> None:
        update_dict = self.model_dump(exclude={"id"})
        dump_and_update_dict(update_dict, "config")
        entity.sqlmodel_update(update_dict)


class ModelUpdate(BaseModel):
    id: int
    name: str | None = Field(max_length=100, default=None)
    enable: bool | None = None

    def update_entity(self, entity: Model) -> None:
        update_dict = self.model_dump(exclude={"id"}, exclude_none=True)
        entity.sqlmodel_update(update_dict)

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if not self.name and self.enable is None:
            raise ValueError("name or enable is required")
        return self


class ModelTestRun(BaseModel):
    id: int
    prompt: str | None = None


class ModelTestRunPublic(BaseModel):
    result: dict  # type: ignore[type-arg]


class SetupDefaultModel(BaseModel):
    workspace_id: int | None = None
    model_type: ModelType
    model_id: int | None = None
    model_name: str | None = None


class ModelChatResult(BaseModel):
    token: str | None = None
    done: bool = False
