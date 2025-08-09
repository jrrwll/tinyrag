from enum import StrEnum


class StorageType(StrEnum):
    S3 = "s3"
    Opendal = "opendal"
