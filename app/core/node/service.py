from app.common.error_code import BizException, ErrorCode
from app.core.node.runner.base import NodeRunner
from app.core.workflow.base import Node


def get_node_runner(node: Node) -> NodeRunner:
    node_type = node.type
    for cls in NodeRunner.implements():
        if cls.get_node_type() == node_type:
            return cls(node)

    raise BizException.create(
        ErrorCode.unknown_error,
        msg=f"NodeRunner implements not found: {node_type}")
