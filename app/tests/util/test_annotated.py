import inspect
from abc import ABC, ABCMeta, abstractmethod
from enum import StrEnum
from typing import Annotated, get_type_hints

from app.core.model.privoder.base import ModelProvider
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


def test_xxx():
    print(f"\n\nimplements:\n{ModelProvider.implements}")

    hints = get_type_hints(Box)
    print(f"\n{hints}")

    annotations = inspect.get_annotations(Box)
    print(f"\n{annotations}")

    print(f"\nplugins:\n{Plugin.plugins}")
    for plugin_cls in Plugin.plugins:
        print(f"{plugin_cls} -> {plugin_cls()}")

    print(f"\nproviders:\n{Plugin.providers}")

    print("\n\n")
    for field_name, field_info in get_extra_schema(NodeSettings).items():
        print(f"{field_name} -> {field_info}")

"""
from cachetools import TTLCache

_cache: TTLCache[int, BaseChatModel] = TTLCache(maxsize=100, ttl=30 * 60)

"""