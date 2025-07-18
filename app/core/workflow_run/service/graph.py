from functools import cached_property
from queue import Queue
from urllib.parse import quote_plus

from app.common.error_code import BizException, ErrorCode
from app.core.node.base import CodeConfig, ConditionConfig, DocExtractConfig, \
    EndConfig, HttpConfig, LLMConfig, StartConfig, TemplateConfig
from app.core.node.service import get_node_runner
from app.core.variable.base import ContextVariable, Variable
from app.core.workflow.base import Edge, WorkflowGraph
from app.core.workflow.enums import NodeType
from app.core.workflow_run.api import NodeRun
from app.util.graph import MutableGraph


class GraphRunner:
    nodes: dict[int, NodeRun]
    graph: MutableGraph[NodeRun, Edge]
    root_node: NodeRun

    output_variables: list[Variable] = []

    def __init__(self, g: WorkflowGraph, input_variables: list[Variable]):
        self.nodes = {node.id: NodeRun.new(node) for node in g.nodes}
        self.graph = self._build_graph(g)
        self.root_node = next(iter(self.graph.root_nodes()))
        self.root_node.input_variables = input_variables

    def run(self) -> None:
        self._traversal(self.root_node)

    def run_node(self, input_variables: list[Variable] | None, node_id: int,
            traversal: bool = False) -> None:
        node = self.nodes.get(node_id)
        if not node:
            raise BizException.new(ErrorCode.model_not_found, node_id)

        node.input_variables = input_variables

        if traversal:
            self._traversal(node)
        else:
            node_runner = get_node_runner(node.node)
            node.output_variables = node_runner.run(node.input_variables)

    def _traversal(self, node: NodeRun) -> None:
        queue = Queue()
        queue.put(node)

        while not queue.empty():
            node = queue.get()
            node_runner = get_node_runner(node.node)

            self._prepare_context_variables(node)
            node.output_variables = node_runner.run(node.input_variables)

            for n in self.graph.successors(node):
                n.input_variables = node.output_variables
                queue.put(n)

    def _prepare_context_variables(self, node: NodeRun) -> None:
        input_variables = node.input_variables
        context_variables = node.node.config.context_variables

        if not context_variables:
            return

        for variable in context_variables:
            target_name = variable.left
            name = variable.right
            node_id = variable.node_id
            if node_id:
                output_variables = self.nodes[node_id].output_variables
                value = next((v.value for v in output_variables
                              if v.name == name), None)
                if value:
                    input_variables.append(Variable(name=target_name, value=value))
            else:
                current_node = node
                while current_node.node.type != NodeType.Start:
                    predecessors = self.graph.predecessors(current_node)
                    if not predecessors:
                        break
                    current_node = next(iter(predecessors))
                    value = next((v.value for v in current_node.output_variables
                                  if v.name == name), None)
                    if value:
                        input_variables.append(Variable(name=target_name, value=value))
                        break

    def _build_graph(self, g: WorkflowGraph) -> MutableGraph[NodeRun, Edge]:
        edges = g.edges

        graph = MutableGraph(self._edge_nodes, self._edge_reverse)
        for node in self.nodes.values():
            graph.add_node(node)
        for edge in edges:
            graph.add_edge(edge)

        return graph

    def _edge_nodes(self, edge: Edge) -> tuple[NodeRun, NodeRun]:
        return (self.nodes[edge.source], self.nodes[edge.target])

    def _edge_reverse(self, edge: Edge) -> Edge:
        edge_dict = edge.model_dump()
        edge_dict.update(source=edge.target, target=edge.source)
        return Edge(**edge_dict)

    @cached_property
    def digraph(self) -> str:
        return self.graph.to_digraph(
            _node_label, node_id=lambda n: n.node.id)

    @property
    def quickchart_url(self) -> str:
        return f"https://quickchart.io/graphviz?graph={quote_plus(self.digraph)}"


def _node_label(n: NodeRun) -> str:
    node = n.node
    s = [f"<{node.type}> {node.name}"]
    node_config = node.config

    match node.type:
        case NodeType.LLM:
            config = LLMConfig.model_validate(node_config)
            s.append(f"\n\nmodel = {config.model_id}")
            s.append(f"\nuser_prompt = ```\n{config.user_prompt}\n```")
            if config.structured_output:
                for st in config.structured_output:
                    s.append(f"\n{st.name}: {st.type} = '{st.description}'")

        case NodeType.Condition:
            config = ConditionConfig.model_validate(node_config)
            s.append(f"\n\nconditions = '{config.conditions}'")

        case NodeType.DocExtract:
            config = DocExtractConfig.model_validate(node_config)
            s.append(f"\n\nextract_file = {config.file}")

        case NodeType.Template:
            config = TemplateConfig.model_validate(node_config)
            s.append(f"\n\ntemplate = ```\n{config.template}\n```\n")
            if config.template_args:
                _fill_variables_str(config.template_args, s)

        case NodeType.Code:
            config = CodeConfig.model_validate(node_config)
            s.append(f"\n\ncode = ```\n{config.code}\n```\n")
            s.append(f"\ncode_args = {config.code_args}")

        case NodeType.HTTP:
            config = HttpConfig.model_validate(node_config)
            s.append(f"\nhttp_config = ```\n{config.http_config.
                     model_dump_json(indent=2).replace('"', '\'')}\n```")

        case NodeType.Start:
            config = StartConfig.model_validate(node_config)
            s.append("\n")
            for v in config.start_variables:
                if v.description:
                    s.append(f"\n{v.name}: {v.type} = '{v.description}'")
                else:
                    s.append(f"\n{v.name}: {v.type}")

        case NodeType.End:
            config = EndConfig.model_validate(node_config)
            s.append("\n")
            _fill_variables_str(config.end_variables, s)

    return "".join(s)


def _fill_variables_str(variables: list[ContextVariable], s: list[str]) -> None:
    for variable in variables:
        sep = f"{variable.node_id}." if variable.node_id else ""
        s.append(f"\n  {variable.left} = {sep}{variable.right}")
