from functools import lru_cache
from typing import Type

from cachetools import TTLCache
from langchain_core.messages import BaseMessage
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.ai import AIMessage

from pydantic import BaseModel, Field
from sqlmodel import Session

from app.common.db import engine
from app.common.error_code import BizException, ErrorCode
from app.core.model.api import ModelPublic
from app.core.model.base import LLMPrompt, ModelParams, StructuredOutput
from app.core.model.enums import PromptRoleType
from app.core.variable.base import Variable
from app.entities.model import Model
from app.util.model import create_model_type


@lru_cache(maxsize=1000)
def get_model(id: int) -> ModelPublic:
    with Session(engine) as session:
        entity = session.get(Model, id)
        if not entity:
            raise BizException.new(ErrorCode.model_not_found, id)

        return ModelPublic.new(entity)


def process_prompt(prompt: LLMPrompt, input_variables: list[Variable]) -> BaseMessage:
    content = prompt.content

    content = content.format(**{var.name: var.value for var in input_variables})
    if prompt.role is PromptRoleType.System:
        return AIMessage(content=content)
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


def process_model_config(params: ModelParams):
    return {}
