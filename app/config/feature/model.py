from pydantic_settings import BaseSettings


class ModelSettings(BaseSettings):

    DEFAULT_TEST_PROMPT: str = "Hi!"
    DEFAULT_NODE_OUTPUT_VARIABLE: str = "result"
