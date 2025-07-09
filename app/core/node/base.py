from enum import StrEnum

from pydantic import BaseModel, Field

from app.core.model.enums import PromptRoleType
from app.core.node.runner.classify import ClassifyTopic, ClassifyVariable
from app.core.variable.base import ContextVariable, InputVariable
from app.core.variable.enums import VariableType, VariableTypeHint


class ExceptionStrategyType(StrEnum):
    DefaultValue = "default_value"
    Node = "node"


class ExceptionDefaultValue(BaseModel):
    name: str
    value: VariableTypeHint


class ExceptionConfig(BaseModel):
    exception_strategy: ExceptionStrategyType
    exception_node_id: int | None = None
    exception_default_values: list[ExceptionDefaultValue] | None = None


class StartConfig(BaseModel):
    start_variables: list[InputVariable]


class EndConfig(BaseModel):
    end_variables: list[ContextVariable]


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


class LLMConfig(BaseModel):
    model_id: int
    model_params: ModelParams | None = None
    user_prompt: str
    advanced_prompts: list[LLMPrompt] | None = None
    structured_output: list[StructuredOutput] | None = None
    context_variables: list[ContextVariable] | None = None
    output_variable: str | None = None

    exception_config: ExceptionConfig | None = None


class HttpMethod(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


# text(like json) -> json

class HttpConfig(BaseModel):
    method: HttpMethod = HttpMethod.POST
    url: str
    headers: dict[str, str] | None = None
    params: dict[str, str] | None = None
    body: str | None = None
    timeout: int | None = Field(default=5, le=30, ge=1)
    context_variables: list[ContextVariable] | None = None
    output_variable: str | None = None

    exception_config: ExceptionConfig | None = None


class ConditionConfig(BaseModel):
    conditions: str
    true_node_id: int
    false_node_id: int


class ClassifyConfig(BaseModel):
    classify_variable: ClassifyVariable
    classify_prompt: str
    classify_topics: list[ClassifyTopic]


class CodeConfig(BaseModel):
    code: str
    code_args: list[ContextVariable]

    exception_config: ExceptionConfig | None = None


class TemplateConfig(BaseModel):
    template: str
    # template_type: TemplateType | None = None
    context_variables: list[ContextVariable] | None = None


class DocExtractConfig(BaseModel):
    file: str

    exception_config: ExceptionConfig | None = None
