from app.config.feature.knowledge import FileUploadSettings, KnowledgeSettings
from app.config.feature.model import ModelSettings
from app.config.feature.storage import StorageSettings


class FeatureSettings(
    ModelSettings,
    FileUploadSettings,
    KnowledgeSettings,
    StorageSettings,
):
    pass
