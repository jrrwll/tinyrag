from enum import StrEnum

BUILTIN_MODEL_PROVIDER_NAME = "builtin"


class ModelType(StrEnum):
    LLM = "llm"
    TextEmbedding = "text_embedding"
    TTS = "tts"
    STT = "stt"


class PromptRoleType(StrEnum):
    System = "system"
    Assistant = "assistant"
    User = "user"


class EmbeddingType(StrEnum):
    Transformer = "transformer"  # sentence-transformers
    Provider = "provider"

    @classmethod
    def is_valid_model_name(cls, model_name: str) -> bool:
        return model_name in _builtin_models[ModelType.TextEmbedding]


_builtin_models = {
    ModelType.TextEmbedding: [
        "all-MiniLM-L6-v2",
        "all-MiniLM-L12-v2",
        "nomic-embed-text-v1",
        "multilingual-e5-small"
    ]
}


def __create_builtin_models_map() -> dict[ModelType, dict[str, int]]:
    mappings =  {}
    seq = 0
    for t, v in _builtin_models.items():
        mappings[t] = {}
        for i in v:
            seq -= 1
            mappings[t][i] = seq
    return mappings


_builtin_models_map = __create_builtin_models_map()


def get_builtin_model_id(model_type: ModelType, model_name: str) -> int | None:
    return _builtin_models_map.get(model_type, {}).get(model_name)
