from app.core.workflow.enums import NodeType
from app.services.node.base import NodeRunner


class LLMNodeRunner(NodeRunner):
    @staticmethod
    def get_node_type() -> NodeType:
        return NodeType.LLM

    def run(self) -> None:
        pass
