from enum import StrEnum


class ModelType(StrEnum):
    LLM = "llm"
    TextEmbedding = "text-embedding"
    TTS = "tts"
    STT = "stt"


class PromptRoleType(StrEnum):
    System = "system"
    Assistant = "assistant"
    User = "user"
