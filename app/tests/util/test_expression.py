from app.util.expression import eval_code

corrected_code = """
def main(arg1: str) -> list[str]:
    body_obj = json.loads(arg1)
    if isinstance(body_obj, dict):
        return [model['name'] for model in body_obj['models']]
    else:
        return body_obj
"""


def test_eval_code():
    arg1 = '{"models": [{"name": "Model1"}, {"name": "Model2"}]}'
    print(f"\narg1: {eval_code(corrected_code, arg1)}")

    arg1_not_dict = '["SingleModel"]'
    print(f"\narg1_not_dict: {eval_code(corrected_code, arg1_not_dict)}")
