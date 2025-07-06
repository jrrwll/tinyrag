from abc import ABCMeta, abstractmethod
from functools import cache
from typing import Type

from app.core.variable.base import Variable
from app.core.workflow.base import Node
from app.core.workflow.enums import NodeType
from app.util.metadata import walk_packages


class NodeRunnerRegistry(ABCMeta):

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if not hasattr(cls, "_implements"):
            cls._implements = []
        else:
            cls._implements.append(cls)


class NodeRunner(metaclass=NodeRunnerRegistry):

    node: Node

    def __init__(self, node: Node):
        self.node = node

    @staticmethod
    @abstractmethod
    def get_node_type() -> NodeType:
        pass

    @abstractmethod
    def run(self, input_variables: list[Variable]) -> list[Variable]:
        pass

    @cache
    @staticmethod
    def implements() -> list[Type["NodeRunner"]]:
        import app.core.node.runner as _runner
        walk_packages(_runner)
        return NodeRunner._implements
