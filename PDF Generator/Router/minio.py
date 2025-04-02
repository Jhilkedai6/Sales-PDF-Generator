from minio import Minio
import io

Endpoint = "127.0.0.1:9000"
Access_key = "minioadmin"
screate_key = "minioadmin"
Bucket_name = "pdf"

# Initialize MinIO client
minio_client = Minio(
    endpoint=Endpoint,
    access_key=Access_key,
    secret_key=screate_key,
    secure=False
)

async def uplode_file(file_name: str, file_bytes: bytes):
    """ Upload PDF file to MinIO and return URL """

    file_like = io.BytesIO(file_bytes)
    file_like.seek(0)  # Ensure we start reading from the beginning

    # Upload file
    minio_client.put_object(
        bucket_name=Bucket_name,
        object_name=file_name,
        data=file_like,
        content_type="application/pdf",
        length=len(file_bytes)  # Keep length but make sure it's bytes, not file-like
    )

    # Return file details
    return {
        "url": f"http://{Endpoint}/{Bucket_name}/{file_name}",
        "document_name": file_name,
        "document_type": "application/pdf"
    }
