import json
from pathlib import Path

from app.core.workflow.api import WorkflowCreate
from app.core.workflow.base import WorkflowGraph
from app.core.workflow_run.service.graph import GraphRunner

_http_dir = (Path(__file__).parent.parent.parent.parent.parent.
             joinpath("dev/http"))


def _load_demo_graph(json_file: str) -> WorkflowGraph:
    text = _http_dir.joinpath(json_file).read_text()

    envs = json.loads(
        _http_dir.joinpath('http-client.private.env.json').read_text())
    for env in envs.values():
        for k, v in env.items():
            text = text.replace("{{"+ k + "}}", v)
    return WorkflowCreate.model_validate_json(text).graph


demo_graphs = [
    _load_demo_graph(j)
    for j in ["workflow_demo1.json", "workflow_demo2.json"]
]


def test_graph():
    for graph in demo_graphs:
        print(graph.model_dump_json())

        runner = GraphRunner(graph, [])
        print(runner.digraph)
        print(runner.quickchart_url)
