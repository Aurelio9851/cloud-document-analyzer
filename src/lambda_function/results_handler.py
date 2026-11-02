
import json
import os
import boto3

textract = boto3.client("textract")
s3 = boto3.client("s3")

BUCKET_NAME = os.environ["BUCKET_NAME"]


def get_document_results(job_id):

    blocks = []
    next_token = None

    while True:

        params = {
            "JobId": job_id,
            "MaxResults": 1000
        }

        if next_token:
            params["NextToken"] = next_token

        response = textract.get_document_analysis(**params)

        status = response["JobStatus"]

        if status not in ("SUCCEEDED", "PARTIAL_SUCCESS"):
            raise RuntimeError(
                f"Unexpected Textract job status: {status}"
            )

        blocks.extend(response.get("Blocks", []))

        next_token = response.get("NextToken")

        if not next_token:
            break

    return blocks


def save_result(job_id, result):

    output_key = f"processed/{job_id}.json"

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=output_key,
        Body=json.dumps(result).encode("utf-8"),
        ContentType="application/json"
    )

    print(
        f"Results saved to s3://{BUCKET_NAME}/{output_key}"
    )


def process_notification(notification):

    job_id = notification.get("JobId")
    status = notification.get("Status")
    job_tag = notification.get("JobTag", job_id)

    if not job_id:
        raise ValueError("Missing JobId in Textract notification")

    print(f"Processing Textract job: {job_id}")
    print(f"Textract status: {status}")

    # Terminal failure: save the error and acknowledge the message.
    if status == "FAILED":

        result = {
            "job_id": job_id,
            "job_tag": job_tag,
            "status": "FAILED",
            "status_message": notification.get(
                "StatusMessage",
                "Textract analysis failed"
            )
        }

        save_result(job_id, result)

        return

    if status not in ("SUCCEEDED", "PARTIAL_SUCCESS"):
        raise RuntimeError(
            f"Unexpected notification status: {status}"
        )

    blocks = get_document_results(job_id)

    result = {
        "job_id": job_id,
        "job_tag": job_tag,
        "status": status,
        "block_count": len(blocks),
        "blocks": blocks
    }

    save_result(job_id, result)


def lambda_handler(event, context):

    print("Received SQS event:")
    print(json.dumps(event))

    batch_item_failures = []

    for record in event["Records"]:

        message_id = record["messageId"]

        try:

            # Extract SNS envelope from the SQS message.
            message = json.loads(record["body"])

            notification = json.loads(message["Message"])

            process_notification(notification)

        except Exception as error:

            print(
                f"Error processing SQS message {message_id}: {error}"
            )

            batch_item_failures.append({
                "itemIdentifier": message_id
            })

    return {
        "batchItemFailures": batch_item_failures
    }
