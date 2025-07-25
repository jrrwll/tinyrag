import json
from typing import Any


# {"a": "[1]"} -> {"a": [1]}
def load_and_update_dict(d: dict[str, Any], *keys: str) -> None:
    new_dict = {}
    for key in keys:
        if key in d:
            new_dict[key] = json.loads(d[key])
    d.update(new_dict)


# {"a": [1]} -> {"a": "[1]"}
def dump_and_update_dict(d: dict[str, Any], *keys: str) -> None:
    new_dict = {}
    for key in keys:
        if key in d:
            new_dict[key] = json.dumps(d[key])
    d.update(new_dict)
