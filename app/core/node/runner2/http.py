import json
from typing import Type
from urllib.parse import quote_plus

import requests

from app.core.node.base import HttpConfig
from app.core.node.runner.base import NodeRunner
from app.core.variable.base import Variable
from app.core.workflow.enums import NodeType


class HttpNodeRunner(NodeRunner):

    @staticmethod
    def get_node_type() -> NodeType:
        return NodeType.HTTP

    @staticmethod
    def get_config_type() -> Type[HttpConfig]:
        return HttpConfig

    def run(self, input_variables: list[Variable]) -> list[Variable]:
        resp = request(self.config)
        status_code = resp.status_code
        text = resp.text

        vars = [
            Variable(name="status_code", value=status_code),
            Variable(name="headers", value=dict(resp.headers)),
            Variable(name="raw_text", value=text),
        ]
        if text:
            try:
                json_val = json.loads(text)
                vars.append(Variable(name="json", value=json_val))
            except Exception as e:
                vars.append(Variable(name="json_parse_error", value=str(e)))
        return vars


def request(http_config: HttpConfig) -> requests.Response:
    method = http_config.method.value()
    url = http_config.request_url

    headers = http_config.headers
    body = http_config.body
    if headers:
        headers = {k.lower(): v for k, v in headers.items()}

    if body:
        body = body.encode("utf-8")
        if headers and 'content-length' not in headers:
            headers['content-type'] = 'application/json; charset=utf-8'

    timeout = http_config.timeout
    return requests.request(
        method=method, url=url,
        headers=headers, data=body,
        timeout=(timeout, timeout))
