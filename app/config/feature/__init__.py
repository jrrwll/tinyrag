from app.config.feature.dataset import DatasetConfig, VectorStoreConfig
from app.config.feature.model import ModelConfig


class FeatureConfig(ModelConfig, DatasetConfig, VectorStoreConfig):
    pass
