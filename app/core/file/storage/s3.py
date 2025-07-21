from typing import Generator

import boto3
from botocore.exceptions import NoCredentialsError
from mypy_boto3_s3 import ListObjectsV2Paginator, S3Client
from mypy_boto3_s3.type_defs import CommonPrefixTypeDef, ObjectTypeDef

from app.config import settings
from app.core.file.storage.base import FileEntry, StorageProvider


class S3StorageProvider(StorageProvider):
    client: S3Client
    bucket: str

    def __init__(self):
        self.client = boto3.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT,
            region_name=settings.S3_REGION,
            access_key_id=settings.S3_KEY_ID,
            secret_access_key=settings.S3_ACCESS_KEY,
        )
        self.bucket = settings.S3_BUCKET_NAME

    def test_connect(self) -> None:
        try:
            res = self.client.list_buckets()
            buckets = res.get('Buckets')
            if self.bucket not in buckets:
                raise Exception(
                    f"bucket {self.bucket} is not found in {buckets}")
        except NoCredentialsError as e:
            raise Exception(f"S3 credentials not available: {e}")

    def list_files(self, prefix: str, recursive: bool = False) -> Generator[
        FileEntry, None, None]:
        delimiter = "/" if not recursive else ""

        paginator: ListObjectsV2Paginator = self.client.get_paginator(
            "list_objects_v2")
        for page in paginator.paginate(
                Bucket=self.bucket, Prefix=prefix, Delimiter=delimiter):
            common_prefixes: list[CommonPrefixTypeDef] = page.CommonPrefixes
            contents: list[ObjectTypeDef] = page.Contents

            # sub dirs
            if common_prefixes:
                for cp in common_prefixes:
                    yield FileEntry(key=cp.Prefix, is_dir=True)

            # files
            if contents:
                for obj in contents:
                    yield FileEntry(key=obj.Key, size=obj.Size,
                                    last_modified=obj.LastModified)

    def download_file(self, key: str, local_path: str) -> None:
        self.client.download_file(self.bucket, key, local_path)

    def upload_file(self, key: str, local_path: str):
        self.client.upload_file(local_path, self.bucket, key)
