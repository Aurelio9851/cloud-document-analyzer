import json
import os
import boto3

from urllib.parse import unquote_plus
from document_processor import process_document

s3 = boto3.client("s3")


def lambda_handler(event, context):

    print("Received event:")
    print(json.dumps(event))

    # Handle native S3 events
    if "Records" in event:

        results = []

        for record in event["Records"]:

            bucket = record["s3"]["bucket"]["name"]

            object_key = unquote_plus(
                record["s3"]["object"]["key"]
            )

            print(f"Processing s3://{bucket}/{object_key}")

            result = process_document(
                s3_client=s3,
                bucket=bucket,
                object_key=object_key
            )
            
            print("Document processing result:")
            print(json.dumps(result, indent=2))

            results.append(result)

        return {
            "statusCode": 200,
            "body": json.dumps(results)
        }

    # Handle manual test events
    bucket = event.get("bucket", os.environ["BUCKET_NAME"])
    object_key = event["object_key"]

    result = process_document(
        s3_client=s3,
        bucket=bucket,
        object_key=object_key
    )

    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }