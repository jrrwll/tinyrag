from typing import Type

from app.core.model.base import LLMPrompt
from app.core.model.enums import PromptRoleType
from app.core.model.llm.base import get_llm_provider
from app.core.model.service import create_structured_output_type, get_model, \
    process_prompt
from app.core.node.base import LLMConfig
from app.core.node.runner.base import NodeRunner
from app.core.variable.base import Variable
from app.core.workflow.enums import NodeType


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

        model = get_model(model_id)
        model_provider = get_llm_provider(model)

        if self.config.structured_output:
            structured_output_type = create_structured_output_type(
                self.node.id, self.config.structured_output)
            return model_provider.run_structured_output(
                model_params, messages, structured_output_type)
        else:
            content = model_provider.run(model_params, messages)
            return [Variable(name=self.config.output_variable, value=content)]
