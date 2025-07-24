from app.core.model.default_model import get_default_model_provider
from app.core.model.enums import ModelType


def test_model_test():
    model_provider = get_default_model_provider(ModelType.LLM)
    print(f"\ntest_run, model_provider={model_provider}")

    res = model_provider.test_run("Who are you?")
    print(f"\nres:\n{res}")
    print(f"content:\n{res.get('content')}")
