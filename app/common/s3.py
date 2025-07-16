import boto3
from botocore.exceptions import NoCredentialsError
from mypy_boto3_s3 import S3Client

from app.config import settings


def create_s3_client() -> S3Client:
    client = boto3.client('s3',
                          endpoint_url=settings.S3_ENDPOINT_URL,
                          aws_access_key_id=settings.S3_ACCESS_KEY,
                          aws_secret_access_key=settings.S3_SECRET_KEY,
                          )
    try:
        response = s3_client.list_buckets()
        buckets = response['Buckets']
        if settings.S3_UPLOAD_BUCKET not in buckets:
            raise Exception(
                f"S3_UPLOAD_BUCKET {settings.S3_UPLOAD_BUCKET} is not found in {buckets}")
    except NoCredentialsError as e:
        raise Exception(f"S3 credentials not available: {e}")
    return client


s3_client = create_s3_client()


def upload_file(file_path: str):
    try:
        s3_client.upload_file(file_path, settings.S3_UPLOAD_BUCKET, 'file_in_s3.txt')
        print("File uploaded successfully.")
    except Exception as e:
        print(f"Error occurred: {e}")
