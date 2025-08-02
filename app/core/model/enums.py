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
