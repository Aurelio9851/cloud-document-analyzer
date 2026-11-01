import json
import os
import boto3

from document_processor import process_document

s3 = boto3.client("s3")


def lambda_handler(event, context):

    print("Received event:")
    print(json.dumps(event))

    bucket = event.get("bucket", os.environ["BUCKET_NAME"])
    object_key = event["object_key"]

    print(f"Processing s3://{bucket}/{object_key}")

    result = process_document(
        s3_client=s3,
        bucket=bucket,
        object_key=object_key
    )

    print("Document processed:")
    print(json.dumps(result))

    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }