import json
from functools import cached_property
from typing import Self

from pydantic_settings import BaseSettings
from pydantic import model_validator

from app.core.dataset.base import ProcessRule


_dataset_default_process_rule = {
    "text_splitter": {
        "chunk_overlap": 50,
        "chunk_size": 1024,
        "separators": ["\n\n", "\n", " ", ""]
    }
}

class DatasetConfig(BaseSettings):
    DATASET_DEFAULT_PROCESS_RULE: str = json.dumps(_dataset_default_process_rule)

    @cached_property
    def dataset_default_process_rule(self) -> ProcessRule:
        return ProcessRule.model_validate_json(
            self.DATASET_DEFAULT_PROCESS_RULE)

    @model_validator(mode="after")
    def _validate_process_rule(self) -> Self:
        process_rule = self.dataset_default_process_rule
        assert process_rule
        return self
