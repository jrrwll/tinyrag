from abc import ABCMeta, abstractmethod
from functools import cache
from typing import Tuple, Type

from app.core.variable.base import Variable
from app.core.workflow.base import Node
from app.core.workflow.enums import NodeType
from app.util.metadata import walk_packages
from pydantic import BaseModel


class NodeRunnerRegistry(ABCMeta):

    def __init__(cls, name, bases, attrs): # type: ignore[no-untyped-def]
        super().__init__(name, bases, attrs)
        if not hasattr(cls, "_implements"):
            cls._implements = []
        else:
            cls._implements.append(cls)
        if not hasattr(cls, "_mappings"):
            cls._mappings = {}
        else:
            cls._mappings[cls.get_node_type()] = cls.get_config_type()


class NodeRunner[T: BaseModel](metaclass=NodeRunnerRegistry):

    def __init__(self, node: Node):
        self.node: Node = node
        self.config: T = self.get_config_type().model_validate(node.config)

    @staticmethod
    @abstractmethod
    def get_node_type() -> NodeType:
        pass

    @staticmethod
    @abstractmethod
    def get_config_type() -> Type[T]:
        pass

    @abstractmethod
    def run(self, input_variables: list[Variable]) -> list[Variable]:
        pass

    @staticmethod
    def implements() -> list[Type["NodeRunner"]]:
        implements, _ = NodeRunner.implements_and_mappings()
        return implements

    @staticmethod
    def mappings() -> dict[NodeType, Type[BaseModel]]:
        _, mappings = NodeRunner.implements_and_mappings()
        return mappings

    @cache
    @staticmethod
    def implements_and_mappings() -> Tuple[list[Type["NodeRunner"]], dict[NodeType, Type[BaseModel]]]:
        import app.core.node.runner as _runner

        walk_packages(_runner)
        return NodeRunner._implements, NodeRunner._mappings # type: ignore[return-value]
