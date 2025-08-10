import inspect
from abc import ABC, ABCMeta, abstractmethod
from enum import StrEnum
from typing import Annotated, get_type_hints

from pydantic import BaseModel, PositiveInt

from app.core.model.embedding.base import EmbeddingProvider
from app.core.model.embedding.transformer import TransformerEmbeddingProvider
from app.core.model.provider import ModelProvider
from app.core.node.base import LLMConfig
from app.core.node.runner.base import NodeRunner
from app.util.lang import find_sub_types, strip_type, walk_and_import_modules
from app.util.model import get_extra_schema


class Type(StrEnum):
    A = "a"
    B = "b"
    C = "c"
    D = "d"


class Box(BaseModel):
    type: str = Annotated[str, "a,b"]
    value: str = Annotated[str, "c,d"]
    name: str = Annotated[str, Type.A, Type.B]
    port: PositiveInt | None = None


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


def test_walk_and_import_modules1():
    print("\nwalk_and_import_modules")
    import app.core.model as model

    for m in walk_and_import_modules(model):
        for attr_name in dir(m):
            attr = getattr(m, attr_name)
            if isinstance(attr, type):
                print(attr)


def test_walk_and_import_modules2():
    print(f"\nimplements:\n{NodeRunner._implements}")

    import app.core.node.runner as runner

    for _ in walk_and_import_modules(runner):
        pass
    print(f"\nwalk_and_import_modules:\n{NodeRunner._implements}")

    implements = find_sub_types(NodeRunner, runner)
    print(f"\nfind_sub_types:\n{implements}")


def test_find_sub_types():
    print("\nfind_sub_types")
    from app.core import model as model_mod

    provider_classes = find_sub_types(ModelProvider, model_mod)
    for cls in provider_classes:
        print(cls)

    print("\nissubclass for ABC")
    print(f"EmbeddingProvider: {issubclass(EmbeddingProvider, ABC)}")
    print(f"{EmbeddingProvider.__bases__} {ABC in EmbeddingProvider.__bases__}")
    print(f"TransformerEmbeddingProvider: "
          f"{issubclass(TransformerEmbeddingProvider, ABC)}")
    print(f"{TransformerEmbeddingProvider.__bases__} "
          f"{ABC in TransformerEmbeddingProvider.__bases__}")
    print("\nexclude_abc")
    provider_classes = find_sub_types(
        ModelProvider, model_mod, exclude_abc=True)
    for cls in provider_classes:
        print(cls)


def test_strip_type():
    print(f"\nBox: {strip_type(Box)}")
    for name, info in Box.model_fields.items():
        print(f"{name}: {strip_type(info.annotation)}")
