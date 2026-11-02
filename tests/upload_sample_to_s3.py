
import boto3
from pathlib import Path

PROFILE = "cda-dev"
REGION = "eu-west-1"

BUCKET_NAME = "cloud-document-analyzer-562912537127-77ebe154"
LOCAL_FILE = Path("docs/samples/sample-document.pdf")
S3_KEY = "uploads/sample-document.pdf"

session = boto3.Session(
    profile_name=PROFILE,
    region_name=REGION
)

s3 = session.client("s3")

if not LOCAL_FILE.exists():
    raise FileNotFoundError(LOCAL_FILE)

s3.upload_file(
    str(LOCAL_FILE),
    BUCKET_NAME,
    S3_KEY
)

print("Upload completed successfully.")
print(f"S3 location: s3://{BUCKET_NAME}/{S3_KEY}")
