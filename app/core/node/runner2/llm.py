from typing import Type

from cachetools import TTLCache
from langchain_core.messages import BaseMessage
from langchain_core.messages.system import SystemMessage
from langchain_core.messages.ai import AIMessage
from langchain_core.messages.human import HumanMessage
from pydantic import BaseModel, Field

from app.core.model.api import ModelPublic
from app.core.model.base import LLMPrompt
from app.core.model.base import StructuredOutput
from app.core.model.enums import PromptRoleType
from app.core.model.llm.base import get_llm_provider
from app.core.node.base import ExceptionConfig, ModelParams
from app.core.node.runner2.base import NodeRunner
from app.core.variable.base import ContextVariable, Variable
from app.core.workflow.enums import NodeType
from app.entities.dao.model import get_model_required
from corepy.model import create_model_type


class LLMConfig(BaseModel):
    model_id: int
    model_params: ModelParams | None = None
    user_prompt: str
    advanced_prompts: list[LLMPrompt] | None = None
    structured_output: list[StructuredOutput] | None = None
    context_variables: list[ContextVariable] | None = None
    output_variable: str | None = None

    exception_config: ExceptionConfig | None = None


class LLMNodeRunner(NodeRunner):

    @staticmethod
    def get_node_type() -> NodeType:
        return NodeType.LLM

    @staticmethod
    def get_config_type() -> Type[LLMConfig]:
        return LLMConfig

    def run(self, input_variables: list[Variable]) -> list[Variable]:
        model_id = self.config.model_id
        model_params = self.config.model_params
        user_prompt = self.config.user_prompt
        advanced_prompts = self.config.advanced_prompts

        prompts = list(advanced_prompts if advanced_prompts else [])
        prompts.append(LLMPrompt(role=PromptRoleType.User, content=user_prompt))
        messages = [process_prompt(prompt, input_variables)
                    for prompt in prompts]

        model = get_model_required(model_id)
        model_provider = get_llm_provider(ModelPublic.create(model))

        if self.config.structured_output:
            structured_output_type = create_structured_output_type(
                self.node.id, self.config.structured_output)
            return model_provider.run_structured_output(
                model_params, messages, structured_output_type)
        else:
            content = model_provider.run(model_params, messages)
            return [Variable(name=self.config.output_variable, value=content)]


def process_prompt(prompt: LLMPrompt,
        input_variables: list[Variable]) -> BaseMessage:
    content = prompt.content

    content = content.format(**{var.name: var.value for var in input_variables})
    if prompt.role is PromptRoleType.System:
        return SystemMessage(content=content)
    elif prompt.role is PromptRoleType.Assistant:
        return AIMessage(content=content)
    else:
        return HumanMessage(content=content)


_structured_output_type_cache: TTLCache[int, Type[BaseModel]] = TTLCache(
    maxsize=1000, ttl=60 * 60)


def create_structured_output_type(node_id: int,
        structured_output: list[StructuredOutput]) -> Type[BaseModel]:
    typ = _structured_output_type_cache.get(node_id)
    if typ is not None:
        return typ

    model_name = f"StructuredOutput{node_id}"
    fields = {so.name: (so.type.to_type(), Field(default=None, description=so.description))
              for so in structured_output}

    typ = create_model_type(
        model_name,
        fields,
        __doc__="dynamic model for structured output"
    )
    _structured_output_type_cache[node_id] = typ
    return typ
