import json
from pathlib import Path

from pydantic import BaseModel, Field

from app.core.model.enums import ModelType


class BuiltinModel(BaseModel):
    id: int = Field(exclude=True)
    vector_size: int
    repo_name: str | None = None


def __create_builtin_models() -> dict[ModelType, dict[str, BuiltinModel]]:
    json_file = Path(__file__).resolve().parent / 'builtin_models.json'
    models = json.loads(json_file.read_text())

    mappings = {}
    seq = 0
    for t, ns in models.items():
        mappings[t] = {}
        for n, m in ns.items():
            seq -= 1
            mappings[ModelType(t)][n] = BuiltinModel(id=seq, **m)
    return mappings


_builtin_models = __create_builtin_models()


def get_builtin_model(model_type: ModelType, model_name: str) -> BuiltinModel | None:
    return _builtin_models.get(model_type, {}).get(model_name)


def is_valid_model_name(model_type: ModelType, model_name: str) -> bool:
    return get_builtin_model(model_type, model_name) is not None
