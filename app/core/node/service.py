from functools import cache, lru_cache
from typing import Type
from pydantic import BaseModel
from app.common.error_code import BizException, ErrorCode
from app.core.node.runner.base import NodeRunner
from app.core.workflow.base import Node
from app.core.workflow.enums import NodeType


@lru_cache(maxsize=1000)
def get_node_runner(node: Node) -> NodeRunner:
    node_type = node.type
    for cls in NodeRunner.implements():
        if cls.get_node_type() == node_type:
            return cls(node)

    raise BizException.new(ErrorCode.unknown_error,
                           f"NodeRunner implements not found: {node_type}")


@cache
def _get_node_allow_type() -> dict[Type[BaseModel], NodeType]:

    all_fields = list(NodeConfig.model_fields.keys())

    fields: dict[NodeType, list[str]] = {}
    for field_name, schema in get_extra_schema(NodeConfig).items():
        allow_types = schema.get("allow_types")
        if allow_types:
            for allow_type in allow_types:
                if allow_type in fields:
                    fields[allow_type].append(field_name)
                else:
                    fields[allow_type] = [field_name]
    for member in NodeType:
        if member not in fields:
            fields[member] = all_fields
    return fields

