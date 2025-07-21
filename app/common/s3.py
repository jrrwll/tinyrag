import boto3
from botocore.exceptions import NoCredentialsError
from mypy_boto3_s3 import S3Client

from app.config import settings


def create_s3_client() -> S3Client:
    client = boto3.client('s3',
                          endpoint_url=settings.S3_ENDPOINT,
                          aws_access_key_id=settings.S3_ACCESS_KEY,
                          aws_secret_access_key=settings.S3_SECRET_KEY,
                          )
    try:
        response = s3_client.list_buckets()
        buckets = response['Buckets']
        if settings.S3_BUCKET_NAME not in buckets:
            raise Exception(
                f"S3_UPLOAD_BUCKET {settings.S3_BUCKET_NAME} is not found in {buckets}")
    except NoCredentialsError as e:
        raise Exception(f"S3 credentials not available: {e}")
    return client


s3_client = create_s3_client()


def upload_file(file_path: str, key: str):
    s3_client.upload_file(file_path, settings.S3_BUCKET_NAME, key)
