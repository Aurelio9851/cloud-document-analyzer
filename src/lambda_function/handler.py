
import json
import os
import boto3

from urllib.parse import unquote_plus
from document_processor import process_document

textract = boto3.client("textract")


def lambda_handler(event, context):

    print("Received event:")
    print(json.dumps(event))

    notification_topic_arn = os.environ["TEXTRACT_NOTIFICATION_TOPIC_ARN"]
    notification_role_arn = os.environ["TEXTRACT_NOTIFICATION_ROLE_ARN"]

    # Handle native S3 events
    if "Records" in event:

        results = []

        for record in event["Records"]:

            bucket = record["s3"]["bucket"]["name"]

            object_key = unquote_plus(
                record["s3"]["object"]["key"]
            )

            print(f"Starting Textract analysis for s3://{bucket}/{object_key}")

            result = process_document(
                textract_client=textract,
                bucket=bucket,
                object_key=object_key,
                notification_topic_arn=notification_topic_arn,
                notification_role_arn=notification_role_arn
            )

            print("Textract job started:")
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
        textract_client=textract,
        bucket=bucket,
        object_key=object_key,
        notification_topic_arn=notification_topic_arn,
        notification_role_arn=notification_role_arn
    )

    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }
