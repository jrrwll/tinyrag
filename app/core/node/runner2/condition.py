from typing import Type

from app.core.node.base import ConditionConfig
from app.core.node.runner.base import NodeRunner
from app.core.variable.base import Variable
from app.core.workflow.enums import NodeType
from app.util.expression import eval_code


class ConditionNodeRunner(NodeRunner[ConditionConfig]):

    @staticmethod
    def get_node_type() -> NodeType:
        return NodeType.Condition

    @staticmethod
    def get_config_type() -> Type[ConditionConfig]:
        return ConditionConfig

    def run(self, input_variables: list[Variable]) -> list[Variable]:
        conditions = self.config.conditions

        kwargs = {var.name: var.value for var in input_variables}

        res = None
        try:
            res = eval_code(conditions, **kwargs)
        except Exception as e:
            raise Exception(f"Error evaluating conditions: {e}")

        if res is True:
            pass
        return input_variables
