import json
from functools import cached_property
from typing import Self

from pydantic import NonNegativeInt, model_validator
from pydantic_settings import BaseSettings

from app.core.knowledge.base import ProcessRule

_default_process_rule = {
    "text_splitter": {
        "chunk_overlap": 50,
        "chunk_size": 1024,
        "separators": ["\n\n", "\n", " ", ""]
    }
}


class KnowledgeSettings(BaseSettings):
    DEFAULT_PROCESS_RULE: str = json.dumps(_default_process_rule)

    @cached_property
    def default_process_rule(self) -> ProcessRule:
        return ProcessRule.model_validate_json(self.DEFAULT_PROCESS_RULE)

    @model_validator(mode="after")
    def _validate_process_rule(self) -> Self:
        assert self.default_process_rule
        ProcessRule.model_validate_json(self.DEFAULT_PROCESS_RULE)
        return self


class FileUploadSettings(BaseSettings):
    UPLOAD_FILE_SIZE_LIMIT: NonNegativeInt = 20
    UPLOAD_IMAGE_FILE_SIZE_LIMIT: NonNegativeInt = 20
    UPLOAD_AUDIO_FILE_SIZE_LIMIT: NonNegativeInt = 50
    UPLOAD_VIDEO_FILE_SIZE_LIMIT: NonNegativeInt = 100
