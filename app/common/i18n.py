import json
from typing import Any, Self

from pydantic import BaseModel

from app.config import settings
from app.util.collection import deep_merge_dict
from app.util.file import load_properties
from app.util.model import model_validate_dict

_i18n_dir = settings.ROOT_DIR() / "i18n"


class I18nBaseField(BaseModel):
    display_name: str | None = None
    description: str | None = None


class I18nBaseEntity(BaseModel):
    display_name: str | None = None
    description: str | None = None
    icon: str | None = None
    fields: dict[str, I18nBaseField] | None = None


class I18nMetaManager:
    """singleton"""
    _instance: Self = None  # type: ignore[assignment]

    def error_codes(self, lang: str | None = None) -> dict[str, str]:
        return self._match_lang(self._error_code, lang)

    def model_providers(self,
            lang: str | None = None) -> dict[str, dict[str, I18nBaseEntity]]:
        return self._match_lang(self._model_providers, lang)

    def vector_store_providers(
            self, lang: str | None = None) -> dict[str, I18nBaseEntity]:
        return self._match_lang(self._vector_store_providers, lang)

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._error_code = self._parse_properties("error_code")
        self._model_providers = {lang: model_validate_dict(d, I18nBaseEntity)
                                 for lang, d in
                                 self._parse_json("model_providers").items()}
        self._vector_store_providers = model_validate_dict(self._parse_json(
            "vector_store_providers"), I18nBaseEntity)

    # navigator.language: zh-CN
    @staticmethod
    def _match_lang(msgs: dict[str, Any], lang: str | None = None) -> Any:
        if lang in msgs:
            return msgs[lang]
        elif '-' in lang:
            lang, tag = lang.split('-', 1)
            specific_lang = f"{lang}_{tag}"
            if specific_lang in msgs:
                return msgs[specific_lang]
            elif lang in msgs:
                return msgs[lang]

        if settings.DEFAULT_LANG in msgs:
            return msgs[settings.DEFAULT_LANG]
        return msgs["default"]

    @staticmethod
    def _parse_json(base_name: str) -> dict[str, dict]:
        msgs = {}
        default_path = _i18n_dir / f"{base_name}.json"
        msgs["default"] = json.loads(default_path.read_text())

        paths = list(_i18n_dir.glob(f"{base_name}_*.json"))
        for p in paths:
            lang = p.stem.split('_', 1)[-1]
            msgs[lang] = json.loads(p.read_text())
            msgs[lang] = deep_merge_dict(msgs["default"], msgs[lang])

        return msgs

    @staticmethod
    def _parse_properties(base_name: str) -> dict[str, dict[str, str]]:
        msgs = {}
        default_path = _i18n_dir / f"{base_name}.properties"
        msgs["default"] = load_properties(default_path)

        paths = list(_i18n_dir.glob(f"{base_name}_*.properties"))
        for p in paths:
            lang = p.stem.split('_', 1)[-1]

            msgs[lang] = load_properties(p)
            msgs[lang] = deep_merge_dict(msgs["default"], msgs[lang])

        return msgs
