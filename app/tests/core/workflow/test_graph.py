from pathlib import Path

from app.core.workflow.api import WorkflowCreate
from app.core.workflow_run.service.graph import GraphRunner

http_dir = Path(__file__).parent.parent.parent.parent.parent.joinpath("dev/http")


def test_graph():
    json_files = ["workflow_demo1.json", "workflow_demo2.json"]

    for j in json_files:
        p = http_dir.joinpath(j)
        print(p)

        w = WorkflowCreate.model_validate_json(p.read_text())
        d = GraphRunner(w.graph)
        print(d.digraph)
        print(d.quickchart_url)
        print(w.graph.model_dump_json())
