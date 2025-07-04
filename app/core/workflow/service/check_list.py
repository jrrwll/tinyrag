from typing import Annotated

from app.common.deps import SessionDep
from app.core.workflow.api import NodeCheckListPublic, WorkflowCheckListPublic, \
    WorkflowPublic
from app.core.workflow.base import NodeSettings
from app.core.workflow.enums import NodeType
from app.entities.model import Model
from app.entities.workflow import Workflow
from app.util.metadata import get_extra_schema
from functools import cache


def workflow_check_list(session: SessionDep, entity: Workflow) -> WorkflowCheckListPublic:
    w = WorkflowPublic.new(entity)
    g = w.graph

    nodes = []
    for n in g.nodes:
        node = NodeCheckListPublic(
            id=n.id, name=n.name
        )
        nodes.append(nodes)

        find_missing_fields(node, n.type, n.settings)

        find_broken_relations(node, n.settings, session)

    return WorkflowCheckListPublic(id=w.id, nodes=nodes)


def find_missing_fields(node: NodeCheckListPublic,
        node_type: NodeType, settings: NodeSettings):
    allow_type_fields = get_node_allow_type_fields().get(node_type.value())

    settings_dict = settings.model_dump()
    for field_name, field_value in settings_dict.items():
        if field_name in allow_type_fields:
            if field_value is not None:
                continue
            node.missing_fields.append(field_name)


@cache
def get_node_allow_type_fields() -> dict[str, list[str]]:
    all_fields = list(NodeSettings.model_fields.keys())

    fields = {}
    for field_name, schema in get_extra_schema(NodeSettings).items():
        allow_types = schema.get("allow_types")
        if allow_types:
            for allow_type in allow_types:
                if allow_type in fields:
                    fields[allow_type].append(field_name)
                else:
                    fields[allow_type] = [field_name]
    for member in NodeType:
        if member.value() not in fields:
            fields[member.value()] = all_fields
    return fields


def find_broken_relations(node: NodeCheckListPublic,
        settings: NodeSettings, session: SessionDep):
    if settings.model_id:
        model_entity = session.get(Model, settings.model_id)
        if not model_entity:
            node.broken_relations.append("model_id")
