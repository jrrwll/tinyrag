from typing import Generator

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from mypy_boto3_s3 import ListObjectsV2Paginator, S3Client
from mypy_boto3_s3.type_defs import CommonPrefixTypeDef, \
    ObjectTypeDef, PaginatorConfigTypeDef

from app.config import settings
from app.core.file.enums import StorageType
from app.core.file.storage.base import FileEntry, StorageProvider


class S3StorageProvider(StorageProvider):
    client: S3Client
    bucket: str

    @staticmethod
    def get_storage_type() -> StorageType:
        return StorageType.S3

    def __init__(self):
        self.client = boto3.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT,
            region_name=settings.S3_REGION,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
        )
        self.bucket = settings.S3_BUCKET_NAME

    def test_connect(self) -> None:
        try:
            res = self.client.list_buckets()
            buckets = [b.get("Name") for b in res.get("Buckets", [])]
            if self.bucket not in buckets:
                raise Exception(
                    f"bucket {self.bucket} is not found in {buckets}")
        except NoCredentialsError as e:
            raise Exception(f"S3 credentials not available: {e}")

    def exists(self, key_or_prefix: str) -> bool:
        # file
        if not key_or_prefix.endswith('/'):
            try:
                self.client.head_object(
                    Bucket=self.bucket, Key=key_or_prefix)
                return True
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    return False
                raise Exception(
                    f"Error checking S3 object, key={key_or_prefix}: {e}")
        # dir
        else:
            res = self.client.list_objects_v2(
                Bucket=self.bucket, Prefix=key_or_prefix, MaxKeys=1)
            return "Contents" in res or 'CommonPrefixes' in res

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
