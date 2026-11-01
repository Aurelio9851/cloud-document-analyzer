import boto3

PROFILE = "cda-dev"
REGION = "eu-west-1"
STACK_NAME = "cloud-document-analyzer-stack"

session = boto3.Session(
    profile_name=PROFILE,
    region_name=REGION
)

cloudformation = session.client("cloudformation")

response = cloudformation.describe_stacks(
    StackName=STACK_NAME
)

outputs = response["Stacks"][0]["Outputs"]

print("API Gateway outputs:\n")

for output in outputs:
    if output["OutputKey"].startswith("UploadApi"):
        print(f"{output['OutputKey']}: {output['OutputValue']}")