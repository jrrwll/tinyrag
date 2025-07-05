from abc import ABCMeta, abstractmethod

from app.core.workflow.base import Node
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
