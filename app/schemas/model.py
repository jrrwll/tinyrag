from pydantic import BaseModel

from app.core.model.enums import ModelType


class ModelPublic(BaseModel):
    type: ModelType
    enable: bool
    provider_name: str
    model_name: str
    settings: dict | None


class ModelCreate(BaseModel):
    type: ModelType
    provider_name: str
    model_name: str
    settings: dict
