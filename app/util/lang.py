import importlib
import pkgutil
from enum import Enum
from types import ModuleType
from typing import Any, Callable, Type


def enum_values[T: Enum](enum_type: Type[T]) -> list[Any]:
    return [m.value for m in enum_type]


def find_sub_types[T](base_type: Type[T], package: ModuleType) -> list[Type[T]]:
    sub_types: list[Type[T]] = []
    def collect_sub_types(module: ModuleType) -> None:
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, base_type) and attr is not base_type:
                sub_types.append(attr)
    walk_packages(package, collect_sub_types)
    return sub_types


def walk_packages(package: ModuleType, action: Callable[[ModuleType], None] | None = None) ->  None:
    package_name = package.__name__
    for _, module_name, _ in pkgutil.walk_packages(package.__path__):
        module = importlib.import_module(f"{package_name}.{module_name}")
        if action:
            action(module)
