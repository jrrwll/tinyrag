from app.config.feature.knowledge import FileUploadSettings, KnowledgeSettings, \
    VectorStoreSettings
from app.config.feature.model import ModelSettings


class FeatureSettings(
    ModelSettings,
    FileUploadSettings,
    KnowledgeSettings,
    VectorStoreSettings):
    pass
