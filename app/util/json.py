import json
from typing import Any


def load_and_update_dict(d: dict[str, Any], *keys: str) -> None:
    new_dict = {}
    for key in keys:
        if key in d:
            new_dict[key] = json.loads(d[key])
    d.update(new_dict)
