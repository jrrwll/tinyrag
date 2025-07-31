from app.config.feature.knowledge import FileUploadSettings, KnowledgeSettings
from app.config.feature.model import ModelSettings


class FeatureSettings(
    ModelSettings,
    FileUploadSettings,
    KnowledgeSettings):
    pass
