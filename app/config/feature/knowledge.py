from pydantic import NonNegativeInt
from pydantic_settings import BaseSettings

from app.core.knowledge.base import ProcessRule

_default_process_rule = {
    "text_splitter": {
        "type": "text",
        "chunk_overlap": 50,
        "chunk_size": 1024,
        "separators": ["\n\n", "\n", " ", ""]
    }
}


class KnowledgeSettings(BaseSettings):
    DEFAULT_PROCESS_RULE: ProcessRule = ProcessRule.model_validate(_default_process_rule)


class FileUploadSettings(BaseSettings):
    UPLOAD_FILE_SIZE_LIMIT: NonNegativeInt = 20
    UPLOAD_IMAGE_FILE_SIZE_LIMIT: NonNegativeInt = 20
    UPLOAD_AUDIO_FILE_SIZE_LIMIT: NonNegativeInt = 50
    UPLOAD_VIDEO_FILE_SIZE_LIMIT: NonNegativeInt = 100
