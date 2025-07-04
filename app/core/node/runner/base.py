from abc import ABC, ABCMeta, abstractmethod
from functools import lru_cache

from app.common.error_code import BizException, ErrorCode
from app.core.workflow.base import Node, NodeSettings
from app.core.workflow.enums import NodeType


class NodeRunnerRegistry(ABCMeta):

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if not hasattr(cls, "implements"):
            cls.implements = []
        else:
            cls.implements.append(cls)


class NodeRunner(metaclass=NodeRunnerRegistry):

    node: Node

    input_variables: list = []
    output_variables: list = []

    def __init__(self, node: Node):
        self.node = node

    @staticmethod
    @abstractmethod
    def get_node_type() -> NodeType:
        pass

    @abstractmethod
    def run(self) -> None:
        pass


@lru_cache(maxsize=1000)
def get_node_runner(node: Node) -> NodeRunner:
    node_type = node.type
    for cls in NodeRunner.implements:
        if cls.get_node_type() == node_type:
            return cls(node)

    raise BizException.new(ErrorCode.unknown_error,
                       f"NodeRunner implements not found: {node_type}")
