from pydantic import BaseModel

from app.core.model.enums import PromptRoleType
from app.core.variable.enums import VariableType


class ModelParams(BaseModel):
    temperature: float | None = None
    top_k: int | None = None
    top_p: float | None = None
    repeat_penalty: float | None = None
    max_tokens: int | None = None


class LLMPrompt(BaseModel):
    role: PromptRoleType
    content: str


class StructuredOutput(BaseModel):
    name: str
    type: VariableType
    description: str | None = None
    options: list[str] | None = None
