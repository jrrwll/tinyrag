from app.config.feature.dataset import DatasetConfig, FileUploadConfig, \
    VectorStoreConfig
from app.config.feature.model import ModelConfig


class FeatureConfig(ModelConfig, FileUploadConfig, DatasetConfig, VectorStoreConfig):
    pass
