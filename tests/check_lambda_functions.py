
import boto3

from src.config import AWS_PROFILE, AWS_REGION

session = boto3.Session(
    profile_name=AWS_PROFILE,
    region_name=AWS_REGION
)

lambda_client = session.client("lambda")

functions = [
    "cloud-document-analyzer-processor",
    "cloud-document-analyzer-upload-url"
]

for function_name in functions:

    response = lambda_client.get_function(
        FunctionName=function_name
    )

    configuration = response["Configuration"]

    print(f"\nFunction: {configuration['FunctionName']}")
    print(f"State: {configuration['State']}")
    print(f"Runtime: {configuration['Runtime']}")
    print(f"Handler: {configuration['Handler']}")
    print(f"Memory: {configuration['MemorySize']} MB")
    print(f"Timeout: {configuration['Timeout']} seconds")
    print(f"Last update: {configuration['LastUpdateStatus']}")
