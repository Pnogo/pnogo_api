from django.conf import settings
from minio import Minio

_client = None


def get_client():
    global _client
    if _client is None:
        _client = Minio(
            settings.S3_URL,
            access_key=settings.S3_ACCESS,
            secret_key=settings.S3_SECRET,
        )
    return _client


def get_object(key):
    return get_client().get_object(settings.S3_BUCKET, key)


def put_object(key, data):
    get_client().put_object(settings.S3_BUCKET, key, data, -1, part_size=10 * 1024 * 1024)


def delete_object(key):
    get_client().remove_object(settings.S3_BUCKET, key)
