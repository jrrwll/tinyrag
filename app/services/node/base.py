from abc import ABC, abstractmethod

from app.core.workflow.enums import NodeType


class NodeRunner(ABC):
    @staticmethod
    @abstractmethod
    def get_node_type() -> NodeType:
        pass

    @abstractmethod
    def run(self) -> None:
        pass
