from app.core.model.privoder.base import get_model_provider
from app.core.model.service import get_model
from app.core.node.runner.base import NodeRunner
from app.core.variable.service import process_prompt
from app.core.workflow.enums import NodeType


class LLMNodeRunner(NodeRunner):

    @staticmethod
    def get_node_type() -> NodeType:
        return NodeType.LLM

    def run(self) -> None:
        settings = self.node.settings

        model_id = settings.model_id
        model_params = settings.model_params
        prompts = settings.prompts
        structured_output = settings.structured_output

        model = get_model(model_id)
        model_provider = get_model_provider(model)

        prompts = [process_prompt(prompt, self.input_variables) for prompt in prompts]

        self.output_variables = model_provider.run(
            model_params, prompts, structured_output)
