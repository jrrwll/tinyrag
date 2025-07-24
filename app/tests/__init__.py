import time

import pytest


@pytest.fixture(autouse=True)
def print_time(request):
    start = time.perf_counter()
    yield
    cost = time.perf_counter() - start
    print(f"\n[{request.node.name}] {cost:.4f}s")
