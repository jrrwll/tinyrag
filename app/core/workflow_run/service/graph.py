from app.common.error_code import BizException, ErrorCode
from app.core.node.runner.base import get_node_runner
from app.core.workflow.base import Edge
from app.core.workflow_run.api import NodeRun
from app.util.graph import MutableGraph
from queue import Queue


class GraphRunner:
    graph: MutableGraph[NodeRun, Edge]

    nodes: dict[int, NodeRun]
    root_node: NodeRun

    output_variables: list

    def __init__(self, graph: MutableGraph[NodeRun, Edge]):
        self.graph = graph
        self.nodes = {node.id: node for node in self.graph.nodes.keys()}

    def run(self):
        self._prepare_context()

        self._traversal(self.root_node)

    def run_node(self, node_id: int, traversal: bool = False):
        node = self.nodes.get(node_id)
        if not node:
            raise BizException.new(ErrorCode.model_not_found, node_id)

        self._prepare_context()

        if traversal:
            self._traversal(node)
        else:
            node_runner = get_node_runner(node)
            node_runner.run()

    def _traversal(self, node: NodeRun):
        queue = Queue()
        queue.put(node)

        while not queue.empty():
            node = queue.get()
            node_runner = get_node_runner(node)
            node_runner.run()
            queue.put(self.graph.successors(node))

    def _prepare_context(self):
        pass
