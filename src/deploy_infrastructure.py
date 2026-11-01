
import boto3
from botocore.exceptions import ClientError

from config import AWS_PROFILE, AWS_REGION

STACK_NAME = "cloud-document-analyzer-stack"
TEMPLATE_PATH = "infrastructure/lambda.yaml"


def main():
    session = boto3.Session(
        profile_name=AWS_PROFILE,
        region_name=AWS_REGION
    )

    cf = session.client("cloudformation")

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as file:
        template_body = file.read()

    try:
        cf.describe_stacks(StackName=STACK_NAME)
        exists = True
    except ClientError as error:
        if error.response["Error"]["Code"] == "ValidationError":
            exists = False
        else:
            raise

    if exists:
        print(f"Updating stack: {STACK_NAME}")
        cf.update_stack(
            StackName=STACK_NAME,
            TemplateBody=template_body,
            Capabilities=["CAPABILITY_NAMED_IAM"]
        )
    else:
        print(f"Creating stack: {STACK_NAME}")
        cf.create_stack(
            StackName=STACK_NAME,
            TemplateBody=template_body,
            Capabilities=["CAPABILITY_NAMED_IAM"]
        )

    waiter = (
        cf.get_waiter("stack_update_complete")
        if exists
        else cf.get_waiter("stack_create_complete")
    )

    print("Waiting for CloudFormation...")
    waiter.wait(StackName=STACK_NAME)

    print("Infrastructure deployed successfully!")

    response = cf.describe_stacks(StackName=STACK_NAME)
    for output in response["Stacks"][0].get("Outputs", []):
        print(f"{output['OutputKey']}: {output['OutputValue']}")


if __name__ == "__main__":
    main()
