from app.core.model.base import LLMPrompt
from app.core.model.enums import PromptRoleType
from app.core.model.privoder.base import get_model_provider
from app.core.model.service import create_structured_output_type, get_model, \
    process_prompt
from app.core.node.runner.base import NodeRunner
from app.core.variable.base import Variable
from app.core.workflow.enums import NodeType


class LLMNodeRunner(NodeRunner):

    @staticmethod
    def get_node_type() -> NodeType:
        return NodeType.LLM

    def run(self, input_variables: list[Variable]) -> list[Variable]:
        settings = self.node.settings

        model_id = settings.model_id
        model_params = settings.model_params
        user_prompt = settings.user_prompt
        advanced_prompts = settings.advanced_prompts

        prompts = list(advanced_prompts if advanced_prompts else [])
        prompts.append(LLMPrompt(role=PromptRoleType.User, content=user_prompt))
        messages = [process_prompt(prompt, input_variables)
                    for prompt in prompts]

        model = get_model(model_id)
        model_provider = get_model_provider(model)

        if settings.structured_output:
            structured_output_type = create_structured_output_type(
                self.node.id, settings.structured_output)
            return model_provider.run_structured_output(
                model_params, messages, structured_output_type)
        else:
            content = model_provider.run(model_params, messages)
            return [Variable(name=settings.output_variable, value=content)]
