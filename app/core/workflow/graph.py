from urllib.parse import quote_plus

from app.core.workflow.api import Edge, Node, WorkflowGraph
from app.util.graph import MutableGraph


class WorkflowGraphDisplay:
    nodes: dict[int, Node]
    edges: list[Edge]
    graph: MutableGraph[Node, Edge]
    digraph: str

    def __init__(self, g: WorkflowGraph):
        self.nodes = {node.id: node for node in g.nodes}
        self.edges = g.edges

        self.graph = MutableGraph(self._edge_nodes, self._edge_reverse)
        for node in self.nodes.values():
            self.graph.add_node(node)
        for edge in self.edges:
            self.graph.add_edge(edge)

        self.digraph = self.graph.to_digraph(self._node_label, node_id=lambda n: n.id)

    def _edge_nodes(self, edge: Edge) -> tuple[Node, Node]:
        return (self.nodes[edge.source], self.nodes[edge.target])

    def _edge_reverse(self, edge: Edge) -> Edge:
        edge_dict = edge.model_dump()
        edge_dict.update(source=edge.target, target=edge.source)
        return Edge(**edge_dict)

    def _node_label(self, node: Node) -> str:
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

    @property
    def quickchart_url(self) -> str:
        return f"https://quickchart.io/graphviz?graph={quote_plus(self.digraph)}"
