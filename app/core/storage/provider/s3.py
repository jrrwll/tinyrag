from typing import Generator

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from mypy_boto3_s3 import ListObjectsV2Paginator, S3Client
from mypy_boto3_s3.type_defs import CommonPrefixTypeDef, \
    ObjectTypeDef, PaginatorConfigTypeDef
from pydantic import BaseModel, SecretStr

from app.common.constants import APP_NAME
from app.core.storage.api import StoragePublic
from app.core.storage.enums import StorageType
from app.core.storage.provider.base import FileEntry, StorageProvider


class S3StorageConfig(BaseModel):
    endpoint: str
    region: str | None = None
    access_key: SecretStr | None = None
    secret_key: SecretStr | None = None
    bucket_name: str | None = APP_NAME


class S3StorageProvider(StorageProvider[S3StorageConfig, S3Client]):

    def __init__(self, storage: StoragePublic):
        super().__init__(storage)
        self.bucket = self.config.bucket_name

    def _create_client(self) -> S3Client:
        return boto3.client(
            's3',
            endpoint_url=self.config.endpoint,
            region_name=self.config.region,
            aws_access_key_id=self.config.access_key,
            aws_secret_access_key=self.config.secret_key,
        )

    @staticmethod
    def get_storage_type() -> StorageType:
        return StorageType.S3

    @staticmethod
    def get_config_type() -> type[S3StorageConfig]:
        return S3StorageConfig

    def test_connect(self) -> None:
        try:
            res = self.client.list_buckets()
            buckets = [b.get("Name") for b in res.get("Buckets", [])]
            if self.bucket not in buckets:
                raise Exception(
                    f"bucket {self.bucket} is not found in {buckets}")
        except NoCredentialsError as e:
            raise Exception(f"S3 credentials not available: {e}")

    def metadata(self, key_or_prefix: str) -> FileEntry | None:
        # file
        if not key_or_prefix.endswith('/'):
            try:
                head = self.client.head_object(
                    Bucket=self.bucket, Key=key_or_prefix)

                return FileEntry(
                    key=key_or_prefix, size=head.get("ContentLength"),
                    last_modified=head.get("LastModified"),
                    mime_type=head.get("ContentType"))
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    return None
                raise Exception(
                    f"Error checking S3 object, key={key_or_prefix}: {e}")
        # dir
        else:
            res = self.client.list_objects_v2(
                Bucket=self.bucket, Prefix=key_or_prefix, MaxKeys=1)
            if "Contents" in res or 'CommonPrefixes' in res:
                return FileEntry(key=key_or_prefix, is_dir=True)
            else:
                return None

    def list_files(self, prefix: str, recursive: bool = False,
            limit: int | None = None) -> Generator[
        FileEntry, None, None]:
        # s3 must use "" rather "/" to represent root path
        if prefix == "/":
            prefix = ""
        delimiter = "/" if not recursive else ""
        pagination_config = None
        if limit:
            pagination_config = PaginatorConfigTypeDef(MaxItems=limit)

        paginator: ListObjectsV2Paginator = self.client.get_paginator(
            "list_objects_v2")
        for page in paginator.paginate(
                Bucket=self.bucket, Prefix=prefix, Delimiter=delimiter,
                PaginationConfig=pagination_config):
            prefixes: list[CommonPrefixTypeDef] = page.get("CommonPrefixes", [])
            contents: list[ObjectTypeDef] = page.get("Contents", [])

            # sub dirs
            if prefixes:
                for cp in prefixes:
                    prefix = cp.get("Prefix")
                    if prefix:
                        yield FileEntry(key=prefix, is_dir=True)

            # files
            if contents:
                for obj in contents:
                    yield FileEntry(key=obj.get("Key"), size=obj.get("Size"),
                                    last_modified=obj.get("LastModified"))

    def download_file(self, key: str, local_path: str) -> None:
        self.client.download_file(self.bucket, key, local_path)

    def upload_file(self, key: str, local_path: str):
        self.client.upload_file(local_path, self.bucket, key)
