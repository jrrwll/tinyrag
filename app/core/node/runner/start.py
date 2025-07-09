from typing import Type

from app.core.node.runner.base import NodeRunner
from app.core.variable.base import Variable
from app.core.workflow.enums import NodeType
from app.core.node.base import StartConfig


class StartNodeRunner(NodeRunner):

    @staticmethod
    def get_node_type() -> NodeType:
        return NodeType.Start

    @staticmethod
    def get_config_type() -> Type[StartConfig]:
        return StartConfig

    def run(self, input_variables: list[Variable]) -> list[Variable]:
        return input_variables
