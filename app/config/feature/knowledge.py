import json
from functools import cached_property
from typing import Self

from pydantic import NonNegativeInt, model_validator
from pydantic_settings import BaseSettings

from app.core.knowledge.base import ProcessRule

_knowledge_default_process_rule = {
    "text_splitter": {
        "chunk_overlap": 50,
        "chunk_size": 1024,
        "separators": ["\n\n", "\n", " ", ""]
    }
}

class KnowledgeSettings(BaseSettings):
    DATASET_DEFAULT_PROCESS_RULE: str = json.dumps(_knowledge_default_process_rule)

    @cached_property
    def knowledge_default_process_rule(self) -> ProcessRule:
        return ProcessRule.model_validate_json(
            self.DATASET_DEFAULT_PROCESS_RULE)

    @model_validator(mode="after")
    def _validate_process_rule(self) -> Self:
        process_rule = self.knowledge_default_process_rule
        assert process_rule
        return self


class FileUploadSettings(BaseSettings):

    UPLOAD_FILE_SIZE_LIMIT: NonNegativeInt = 20
    UPLOAD_IMAGE_FILE_SIZE_LIMIT: NonNegativeInt = 20
    UPLOAD_AUDIO_FILE_SIZE_LIMIT: NonNegativeInt = 50
    UPLOAD_VIDEO_FILE_SIZE_LIMIT: NonNegativeInt = 100
