from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from minio import Minio
from datetime import timedelta
from ..settings import settings

tags_metadata = [
    {
        "name": "MinIO - MinIO interface",
        "description": "Get/Put data to/from MinIO."
    }
]

router = APIRouter(tags=["MinIO"])


def get_minio_client(internal: bool = True) -> Minio:
    if internal:
        endpoint = "minio:9000"
    else:
        endpoint = settings.minio_host
    client = Minio(
        endpoint=endpoint,
        access_key=settings.minio_username,
        secret_key=settings.minio_password,
        secure=False,
        cert_check=False
    )
    return client


@router.get(
    "/download-link/{bucket_name}/{key_name}"
)
async def get_file_download_link(
    bucket_name: str,
    key_name: str
):
    try:
        minio_client = get_minio_client(internal=False)
        url = minio_client.presigned_get_object(
            bucket_name,
            key_name,
            expires=timedelta(minutes=30)
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=403, detail="Item not found")
    return url


@router.get(
    "/upload-link/{bucket_name}/{key_name}"
)
async def get_file_upload_link(
    bucket_name: str,
    key_name: str
):
    try:
        minio_client = get_minio_client(internal=False)
        url = minio_client.presigned_put_object(
            bucket_name,
            key_name,
            expires=timedelta(minutes=30)
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=403, detail="Item not found")
    return url


@router.get(
    "/{bucket_name}/{key_name}"
)
async def get_file(
    bucket_name: str,
    key_name: str
):
    try:
        minio_client = get_minio_client()
        handle = minio_client.get_object(bucket_name, key_name)
        media_type = handle.headers['Content-Type']
        headers = {
            "Content-Disposition": f"inline; filename=\"{key_name}\""
        }

        def iter():
            for chunk in handle.stream(1024*1024):
                yield chunk
            handle.close()
            handle.release_conn()
        return StreamingResponse(iter(),
                                 media_type=media_type,
                                 headers=headers)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=403, detail="Item not found")


@router.post(
    "/{bucket_name}/{key_name}",
    status_code=200
)
async def upload_file(
    bucket_name: str,
    key_name: str,
    file: UploadFile
):
    try:
        # Using seek is ugly but i don't know a better way right now
        minio_client = get_minio_client()
        file.file.seek(0, 2)
        length = file.file.tell()
        file.file.seek(0)
        minio_client.put_object(bucket_name,
                                key_name,
                                file.file,
                                length=length,
                                content_type=file.content_type)
        return key_name
    except Exception as e:
        print(e)
        raise HTTPException(status_code=403, detail="Item not found")
