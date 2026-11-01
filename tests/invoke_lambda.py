
import boto3
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from config import AWS_PROFILE, AWS_REGION

FUNCTION_NAME = "cloud-document-analyzer-processor"


def main():
    session = boto3.Session(
        profile_name=AWS_PROFILE,
        region_name=AWS_REGION
    )

    lambda_client = session.client("lambda")

    # Simulate an event received by the Lambda function
    event = {
        "event_type": "document_upload",
        "bucket": "cloud-document-analyzer-1793537371",
        "object_key": "uploads/sample.txt"
    }

    response = lambda_client.invoke(
        FunctionName=FUNCTION_NAME,
        InvocationType="RequestResponse",
        Payload=json.dumps(event).encode("utf-8")
    )

    payload = json.loads(response["Payload"].read())

    print("Lambda invocation completed")
    print(f"HTTP status: {response['StatusCode']}")
    print(f"Lambda response: {json.dumps(payload, indent=2)}")

    if "FunctionError" in response:
        raise RuntimeError(
            f"Lambda execution failed: {response['FunctionError']}"
        )


if __name__ == "__main__":
    main()
