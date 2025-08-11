from app.core.meta.provider import MetaProvider, encrypt_config_dict, decrypt_config_dict
from app.core.model.llm.openai import OpenaiModelConfig
from pydantic import SecretStr


def test_crypt_config_dict():
    config_dict = OpenaiModelConfig(
        api_key=SecretStr("sk-xxx")
    ).model_dump()
    config_dict = encrypt_config_dict(OpenaiModelConfig, config_dict)
    print(f"\nencrypt_config_dict: {config_dict}")

    config_dict = decrypt_config_dict(OpenaiModelConfig, config_dict)
    print(f"\ndecrypt_config_dict: {config_dict}")
