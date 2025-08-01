import importlib
import pkgutil
from abc import ABC
from enum import Enum
from types import ModuleType
from typing import Any, Iterable, Type


def enum_values[T: Enum](enum_type: Type[T]) -> list[Any]:
    return [m.value for m in enum_type]


def find_sub_types[T](base_type: Type[T], package: ModuleType,
        exclude_abc: bool = False) -> set[Type[T]]:
    sub_types: set[Type[T]] = set()

    modules = walk_and_import_modules(package)
    for m in modules:
        for attr_name in dir(m):
            attr = getattr(m, attr_name)
            if not isinstance(attr, type):
                continue
            if not issubclass(attr, base_type) or attr is base_type:
                continue
            if attr.__module__ != m.__name__:
                continue
            if exclude_abc and ABC in attr.__bases__:
                continue
            sub_types.add(attr)

    return sub_types


def walk_and_import_modules(package: ModuleType) -> Iterable[ModuleType]:
    for info in pkgutil.iter_modules(package.__path__, package.__name__ + '.'):
        sub_mod = importlib.import_module(info.name)
        if info.ispkg:
            yield from walk_and_import_modules(sub_mod)
        else:
            yield sub_mod
