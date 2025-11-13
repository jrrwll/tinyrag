from corepy.expression import eval_code, eval_main_func

from app.common.error_code import BizException, ErrorCode

corrected_code = """
def main(arg1: str) -> list[str]:
    body_obj = json_loads(arg1)
    if isinstance(body_obj, dict):
        return [model['name'] for model in body_obj['models']]
    else:
        return body_obj
"""

arg1 = '{"models": [{"name": "Model1"}, {"name": "Model2"}]}'
arg1_not_dict = '["SingleModel"]'


def eval_main_func_unwrap(code: str, *args, **kwargs) -> Any: # type: ignore[no-untyped-def]
    try:
        res = eval_main_func(code, *args, **kwargs)
    except Exception as e:
        raise BizException.create(ErrorCode.code_eval_error, msg=str(e))

    if res.is_empty():
        raise BizException.create(ErrorCode.code_main_func_undefined)
    return res.value


def test_eval_main_func():
    print(f"\narg1: {eval_main_func_unwrap(corrected_code, arg1)}")

    print(f"\narg1_not_dict: {eval_main_func_unwrap(corrected_code, arg1_not_dict)}")


def test_eval_code():
    res = eval_code("a > 3 and b is not None", a=4, b=__name__)
    print(f"\nbool expr1: {res}")
    res = eval_code("a > 3 and b is not None", a=10, b=None)
    print(f"\nbool expr2: {res}")

    res = eval_code(f"{corrected_code}\nmain(arg1)", arg1=arg1)
    print(f"\narg1: {res}")

    res = eval_code(f"{corrected_code}\nmain(arg1)", arg1=arg1_not_dict)
    print(f"\narg1_not_dict: {res}")
