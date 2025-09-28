from typing import Type

from app.core.node.base import DocExtractConfig
from app.core.node.runner.base import NodeRunner
from app.core.variable.base import Variable
from app.core.workflow.enums import NodeType


class DocExtractNodeRunner(NodeRunner):

    @staticmethod
    def get_node_type() -> NodeType:
        return NodeType.DocExtract

    @staticmethod
    def get_config_type() -> Type[DocExtractConfig]:
        return DocExtractConfig

    def run(self, input_variables: list[Variable]) -> list[Variable]:
        pass
