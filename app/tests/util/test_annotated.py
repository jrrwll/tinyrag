from enum import StrEnum
from typing import Annotated, get_type_hints
import inspect

from app.core.workflow.base import NodeSettings
from app.util.metadata import get_extra_schema


class Type(StrEnum):
    A = "a"
    B = "b"
    C = "c"
    D = "d"

class Box:

    type: str = Annotated[str, "a,b"]
    value: str = Annotated[str, "c,d"]
    name: str = Annotated[str, Type.A, Type.B]



class PluginRegistry(type):

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if not hasattr(cls, "plugins"):
            cls.plugins = []  # 存储所有插件类
        else:
            cls.plugins.append(cls)  # 注册新插件

class Plugin(metaclass=PluginRegistry):
    pass

class MyPlugin1(Plugin):
    pass

class MyPlugin2(Plugin):
    pass


def test_xxx():
    hints = get_type_hints(Box)
    print(f"\n{hints}")

    annotations = inspect.get_annotations(Box)
    print(f"\n{annotations}")

    print(f"\n{Plugin.plugins}")

    for plugin_cls in Plugin.plugins:
        print(f"{plugin_cls} -> {plugin_cls()}")


    print("\n\n")
    for field_name, field_info in get_extra_schema(NodeSettings).items():
        print(f"{field_name} -> {field_info}")

