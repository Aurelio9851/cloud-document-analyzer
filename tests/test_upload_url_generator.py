
import json
import urllib.request
import urllib.error
import boto3

from src.config import AWS_PROFILE, AWS_REGION

session = boto3.Session(
    profile_name=AWS_PROFILE,
    region_name=AWS_REGION
)

lambda_client = session.client("lambda")

filename = "test_upload.txt"

# 1. Request a presigned URL from Lambda.
response = lambda_client.invoke(
    FunctionName="cloud-document-analyzer-upload-url",
    InvocationType="RequestResponse",
    Payload=json.dumps({
        "body": json.dumps({
            "filename": filename
        })
    })
)

payload = json.loads(response["Payload"].read())

if response.get("FunctionError"):
    raise RuntimeError(f"Lambda execution failed: {payload}")

if payload["statusCode"] != 200:
    raise RuntimeError(f"URL generation failed: {payload}")

body = json.loads(payload["body"])

upload_url = body["upload_url"]
object_key = body["object_key"]

print("Presigned URL generated successfully.")
print("Object key:", object_key)

# 2. Upload the document directly to S3.
document_content = (
    "Cloud Document Analyzer\n\n"
    "This document was uploaded using a presigned URL.\n"
    "The upload was performed directly from the Python client.\n"
)

request = urllib.request.Request(
    upload_url,
    data=document_content.encode("utf-8"),
    method="PUT",
    headers={
        "Content-Type": "text/plain"
    }
)

try:
    with urllib.request.urlopen(request) as upload_response:
        print("\nS3 upload status:", upload_response.status)
        print("Upload completed successfully.")

except urllib.error.HTTPError as error:
    print("Upload failed:", error.code)
    print(error.read().decode("utf-8"))
    raise

print("\nUploaded object:", object_key)
