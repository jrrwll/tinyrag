import json
from typing import Any

from app.common.error_code import BizException, ErrorCode

_safe_globals = {
    "__builtins__": {
        # types
        "str": str,
        "int": int,
        "float": float,
        "list": list,
        "dict": dict,
        "set": set,
        "bool": bool,
        # functions
        "isinstance": isinstance,
        "len": len,
        "sum": sum,
        "max": max,
        "min": min,
    },
    "json": json,
}


# eval main function and return the result
def eval_code(code: str, *args, **kwargs) -> Any:  # type: ignore[no-untyped-def]
    safe_locals = {}  # type: ignore[var-annotated]
    exec(code, _safe_globals, safe_locals)

    main_func = safe_locals.get("main")
    if not main_func:
        raise BizException.new(ErrorCode.code_main_func_undefined)

    try:
        return main_func(*args, **kwargs)
    except Exception as e:
        raise BizException.new(ErrorCode.code_eval_error, str(e))
