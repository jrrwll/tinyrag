import inspect
from abc import ABCMeta, abstractmethod
from enum import StrEnum
from typing import Annotated, get_type_hints

from app.core.node.base import LLMConfig
from app.core.node.runner.base import NodeRunner
from app.util.lang import find_sub_types, walk_packages
from app.util.model import get_extra_schema


class Type(StrEnum):
    A = "a"
    B = "b"
    C = "c"
    D = "d"


class Box:
    type: str = Annotated[str, "a,b"]
    value: str = Annotated[str, "c,d"]
    name: str = Annotated[str, Type.A, Type.B]


def model_provider_registry(cls):
    if not hasattr(cls, 'providers'):
        cls.providers = {}

    cls.providers[cls.__name__.lower()] = cls
    return cls


class PluginRegistry(ABCMeta):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if not hasattr(cls, "plugins"):
            cls.plugins = []  # 存储所有插件类
        else:
            cls.plugins.append(cls)  # 注册新插件


@model_provider_registry
class Plugin(metaclass=PluginRegistry):

    @abstractmethod
    def say(self) -> None:
        pass


@model_provider_registry
class MyPlugin1(Plugin):

    def say(self) -> None:
        print("MyPlugin1")


class MyPlugin2(Plugin):

    def say(self) -> None:
        print("MyPlugin2")


def test_registry():
    hints = get_type_hints(Box)
    print(f"\n{hints}")

    annotations = inspect.get_annotations(Box)
    print(f"\n{annotations}")

    print(f"\nplugins:\n{Plugin.plugins}")
    for plugin_cls in Plugin.plugins:
        print(f"{plugin_cls} -> {plugin_cls()}")

    print(f"\nproviders:\n{Plugin.providers}")

    print("\n\n")
    for field_name, field_info in get_extra_schema(LLMConfig).items():
        print(f"{field_name} -> {field_info}")


def test_walk_packages():
    print(f"\nimplements:\n{NodeRunner._implements}")

    import app.core.node.runner as runner
    implements = find_sub_types(NodeRunner, runner)
    print(f"\nimplements:\n{implements}")

    walk_packages(runner)
    print(f"\nimplements:\n{NodeRunner._implements}")
