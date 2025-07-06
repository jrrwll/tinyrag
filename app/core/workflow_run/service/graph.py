from functools import cached_property
from queue import Queue
from urllib.parse import quote_plus

from app.common.error_code import BizException, ErrorCode
from app.core.node.service import get_node_runner
from app.core.variable.base import Variable
from app.core.workflow.base import Edge, WorkflowGraph
from app.core.workflow_run.api import NodeRun
from app.util.graph import MutableGraph


class GraphRunner:

    nodes: dict[int, NodeRun]
    graph: MutableGraph[NodeRun, Edge]
    root_node: NodeRun

    def __init__(self, g: WorkflowGraph, input_variables: list[Variable]):
        self.nodes = {node.id: NodeRun.new(node) for node in g.nodes}
        self.graph = self._build_graph(g)
        self.root_node = [n for n, d in self.graph.in_degrees().items() if d == 0][0]
        self.root_node.input_variables = input_variables

    def run(self):
        self._traversal(self.root_node)

    def run_node(self, input_variables: list[Variable] | None, node_id: int, traversal: bool = False):
        node = self.nodes.get(node_id)
        if not node:
            raise BizException.new(ErrorCode.model_not_found, node_id)

        node.input_variables = input_variables

        if traversal:
            self._traversal(node)
        else:
            node_runner = get_node_runner(node.node)
            node.output_variables = node_runner.run(node.input_variables)

    def _traversal(self, node: NodeRun):
        queue = Queue()
        queue.put(node)

        while not queue.empty():
            node = queue.get()
            node_runner = get_node_runner(node.node)

            node.output_variables = node_runner.run(node.input_variables)
            for n in self.graph.successors(node):
                n.input_variables = node.output_variables
                queue.put(n)

    def _prepare_context(self):
        pass

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
    settings = node.settings

    if settings.extract_file:
        s.append(f"\n\nextract_file={settings.extract_file}")

    end_variables = settings.end_variables
    if end_variables:
        s.append("\n\nend_variables:")
        for end_variable in end_variables:
            sep = f"{end_variable.node_id}." if end_variable.node_id else ""
            s.append(f"\n {end_variable.name}={sep}{end_variable.value}")

    return "".join(s)
