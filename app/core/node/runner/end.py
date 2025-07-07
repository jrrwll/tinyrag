from app.core.node.runner.base import NodeRunner
from app.core.variable.base import Variable
from app.core.workflow.enums import NodeType


class EndNodeRunner(NodeRunner):

    @staticmethod
    def get_node_type() -> NodeType:
        return NodeType.End

    def run(self, input_variables: list[Variable]) -> list[Variable]:
        return input_variables
