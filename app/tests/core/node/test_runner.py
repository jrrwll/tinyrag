from app.core.node.runner.http import HttpNodeRunner
from app.core.workflow.enums import NodeType
from app.core.workflow_run.service.graph import GraphRunner
from app.tests.core.workflow.test_graph import demo_graphs


def test_http():
    for graph in demo_graphs:
        g = GraphRunner(graph, [])

        http_nodes = [n.node for n in g.nodes.values()
                      if n.node.type == NodeType.HTTP]
        for node in http_nodes:
            runner = HttpNodeRunner(node)
            vars = runner.run([])
            print(f"\nvars:{vars}")
