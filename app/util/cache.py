import time
from functools import wraps


def ttl_cache(ttl_seconds):
    def decorator(func):
        cache = {}
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, frozenset(kwargs.items()))
            if key in cache:
                value, timestamp = cache[key]
                if time.time() - timestamp < ttl_seconds:
                    return value

            value = func(*args, **kwargs)
            cache[key] = (value, time.time())
            return value
        return wrapper
    return decorator
