from enum import StrEnum

SYSTEM_MODEL_PROVIDER_NAME = "system"


class ModelType(StrEnum):
    LLM = "llm"
    TextEmbedding = "text_embedding"
    TTS = "tts"
    STT = "stt"


class PromptRoleType(StrEnum):
    System = "system"
    Assistant = "assistant"
    User = "user"


_TRANSFORMER_MODELS = [
    "all-MiniLM-L6-v2",
    "all-MiniLM-L12-v2",
    "nomic-embed-text-v1",
    "multilingual-e5-small"
]


class EmbeddingType(StrEnum):
    Transformer = "transformer" # sentence-transformers
    Provider = "provider"

    @classmethod
    def is_valid_model_name(cls, model_name: str) -> bool:
        return model_name in _TRANSFORMER_MODELS
