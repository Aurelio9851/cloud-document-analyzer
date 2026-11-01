
import json
import os
import boto3
import re

s3 = boto3.client("s3")

BUCKET_NAME = os.environ["BUCKET_NAME"]
UPLOAD_PREFIX = "uploads/"


def lambda_handler(event, context):

    try:
        body = json.loads(event.get("body") or "{}")

        filename = body.get("filename")

        if not filename:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "filename is required"
                })
            }

        # Accept only simple filenames
        if (
            not isinstance(filename, str)
            or not re.fullmatch(r"[A-Za-z0-9._-]{1,150}", filename)
            or filename in {".", ".."}
        ):
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "Invalid filename"
                })
            }

        object_key = f"{UPLOAD_PREFIX}{filename}"

        presigned_url = s3.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": object_key
            },
            ExpiresIn=300
        )

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "upload_url": presigned_url,
                "object_key": object_key,
                "expires_in": 300
            })
        }

    except Exception as error:
        print(f"Error generating upload URL: {error}")

        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Unable to generate upload URL"
            })
        }
