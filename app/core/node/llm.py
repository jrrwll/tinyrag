from app.core.node.base import NodeRunner
from app.core.workflow.enums import NodeType


class LLMNodeRunner(NodeRunner):
    @staticmethod
    def get_node_type() -> NodeType:
        return NodeType.LLM

    def run(self) -> None:
        pass
