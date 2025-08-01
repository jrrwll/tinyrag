import json
from datetime import datetime

from pydantic import BaseModel

from app.common.constants import MIN_UTC_DATETIME
from app.core.model.enums import BUILTIN_MODEL_PROVIDER_NAME, ModelType, \
    get_builtin_model_id
from app.entities.model import Model
from app.util.codec import md5
from app.util.model import dump_and_update_dict


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
    def create(entity: Model) -> "ModelPublic":
        entity_dict = entity.model_dump(exclude_none=True)
        if entity.config:
            entity_dict['config'] = json.loads(entity.config)

        return ModelPublic(**entity_dict)

    @staticmethod
    def from_builtin(model_type: ModelType, model_name: str) -> "ModelPublic":
        return ModelPublic(
            id=get_builtin_model_id(model_type, model_name),
            created_at=MIN_UTC_DATETIME,
            updated_at=MIN_UTC_DATETIME,
            type=model_type,
            enable=True,
            provider_name=BUILTIN_MODEL_PROVIDER_NAME,
            model_name=model_name,
            config={},
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
    id: int
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
    id: int
    enable: bool


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
