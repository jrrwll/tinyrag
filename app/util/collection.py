import os
from typing import Callable, Iterable


def take_limit[T](iterable: Iterable[T], limit: int) -> list[T]:
    output = []
    for doc in iterable:
        if limit == 0:
            break
        limit -= 1

        output.append(doc)
    return output


def partition_list[T](a: list[T], size: int | None = None) -> list[list[T]]:
    n = len(a)
    if not size:
        cpu_count = os.cpu_count()
        if not cpu_count or cpu_count > n or cpu_count < 2:
            return [a]
        size = n // cpu_count

    output = []
    i, n = 0, len(a)
    while i < n:
        output.append(a[i:i + size])
        i += size
    return output


def partition_iterable[T](a: Iterable[T], size: int) -> Iterable[list[T]]:
    output = []
    for i in a:
        output.append(i)
        if len(output) == size:
            yield output
            output = []
    if output:
        yield output


def any_match[T](iterable: Iterable[T],
        predicate: Callable[[T], bool]) -> T | None:
    for i in iterable:
        if predicate(i):
            return i
    return None
