
import boto3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from config import AWS_PROFILE, AWS_REGION, S3_BUCKET_NAME


def main():
    session = boto3.Session(
        profile_name=AWS_PROFILE,
        region_name=AWS_REGION
    )

    s3 = session.client("s3")

    response = s3.list_objects_v2(
        Bucket=S3_BUCKET_NAME,
        Prefix="uploads/"
    )

    objects = response.get("Contents", [])

    if not objects:
        print("No documents found.")
        return

    print("Documents stored in S3:\n")

    for obj in objects:
        print(f"- {obj['Key']} ({obj['Size']} bytes)")


if __name__ == "__main__":
    main()
