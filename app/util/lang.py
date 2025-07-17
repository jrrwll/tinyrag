from typing import Callable, Iterator
import os


def take_limit[T](iterator: Iterator[T], limit: int) -> list[T]:
    output = []
    for doc in iterator:
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


def any_match[T](iterator: Iterator[T], predicate: Callable[[T], bool]) -> T | None:
    for i in iterator:
        if predicate(i):
            return i
    return None
