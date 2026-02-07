from flask import current_app, g
from minio import Minio


def get_s3():
    if "obj" not in g:
        g.obj = Minio(
            current_app.config["S3_URL"],
            access_key=current_app.config["S3_ACCESS"],
            secret_key=current_app.config["S3_SECRET"],
        )

    return g.obj


def get_object(key):
    return get_s3().get_object(current_app.config["S3_BUCKET"], key)


def put_object(key, obj):
    get_s3().put_object(current_app.config["S3_BUCKET"], key, obj, -1, part_size=10 * 1024 * 1024)


def delete_object(key):
    get_s3().remove_object(current_app.config["S3_BUCKET"], key)
