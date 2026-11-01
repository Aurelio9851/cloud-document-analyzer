
import boto3
from pathlib import Path

from config import (
    AWS_PROFILE,
    AWS_REGION,
    S3_BUCKET_NAME,
    DATA_DIR
)


def upload_document(filename: str):
    file_path = Path(DATA_DIR) / filename

    if not file_path.is_file():
        raise FileNotFoundError(f"Document not found: {file_path}")

    session = boto3.Session(
        profile_name=AWS_PROFILE,
        region_name=AWS_REGION
    )

    s3 = session.client("s3")

    # Store documents in a dedicated S3 prefix
    object_key = f"uploads/{filename}"

    s3.upload_file(
        str(file_path),
        S3_BUCKET_NAME,
        object_key
    )

    print("Upload completed successfully!")
    print(f"Bucket: {S3_BUCKET_NAME}")
    print(f"Object key: {object_key}")


if __name__ == "__main__":
    upload_document("sample.txt")
