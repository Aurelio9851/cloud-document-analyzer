import hashlib
import os
import zipfile

import boto3
from botocore.exceptions import ClientError

from config import (
    AWS_PROFILE,
    AWS_REGION,
    S3_BUCKET_NAME,
    PROJECT_ROOT
)

STACK_NAME = "cloud-document-analyzer-stack"

TEMPLATE_PATH = os.path.join(
    PROJECT_ROOT,
    "infrastructure",
    "lambda.yaml"
)

LAMBDA_SOURCE_DIR = os.path.join(
    PROJECT_ROOT,
    "src",
    "lambda_function"
)

BUILD_DIR = os.path.join(PROJECT_ROOT, "build")


def create_lambda_package():
    """Create a ZIP containing the Lambda source files."""

    os.makedirs(BUILD_DIR, exist_ok=True)

    zip_path = os.path.join(
        BUILD_DIR,
        "lambda_package.zip"
    )

    with zipfile.ZipFile(
        zip_path,
        "w",
        compression=zipfile.ZIP_DEFLATED
    ) as zip_file:

        for filename in sorted(os.listdir(LAMBDA_SOURCE_DIR)):
            file_path = os.path.join(
                LAMBDA_SOURCE_DIR,
                filename
            )

            if filename.endswith(".py") and os.path.isfile(file_path):
                zip_file.write(
                    file_path,
                    arcname=filename
                )

    with open(zip_path, "rb") as file:
        package_hash = hashlib.sha256(file.read()).hexdigest()[:12]

    s3_key = f"deployments/lambda_package_{package_hash}.zip"

    print(f"Lambda package created: {zip_path}")
    print(f"Package SHA-256: {package_hash}")

    return zip_path, s3_key


def upload_lambda_package(s3, zip_path, s3_key):
    """Upload the Lambda ZIP package to S3."""

    print(f"Uploading package to s3://{S3_BUCKET_NAME}/{s3_key}")

    s3.upload_file(
        zip_path,
        S3_BUCKET_NAME,
        s3_key,
        ExtraArgs={
            "ServerSideEncryption": "AES256"
        }
    )

    print("Lambda package uploaded successfully.")


def deploy_stack(cf, s3_key):
    """Create or update the CloudFormation stack."""

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as file:
        template_body = file.read()

    parameters = [
        {
            "ParameterKey": "S3BucketName",
            "ParameterValue": S3_BUCKET_NAME
        },
        {
            "ParameterKey": "LambdaCodeS3Key",
            "ParameterValue": s3_key
        }
    ]

    try:
        cf.describe_stacks(StackName=STACK_NAME)
        stack_exists = True

    except ClientError as error:
        if error.response["Error"]["Code"] == "ValidationError":
            stack_exists = False
        else:
            raise

    if stack_exists:
        print(f"Updating stack: {STACK_NAME}")

        try:
            cf.update_stack(
                StackName=STACK_NAME,
                TemplateBody=template_body,
                Parameters=parameters,
                Capabilities=["CAPABILITY_NAMED_IAM"]
            )

            waiter = cf.get_waiter("stack_update_complete")

        except ClientError as error:
            if "No updates are to be performed" in str(error):
                print("CloudFormation reports that no updates are needed.")
                return

            raise

    else:
        print(f"Creating stack: {STACK_NAME}")

        cf.create_stack(
            StackName=STACK_NAME,
            TemplateBody=template_body,
            Parameters=parameters,
            Capabilities=["CAPABILITY_NAMED_IAM"]
        )

        waiter = cf.get_waiter("stack_create_complete")

    print("Waiting for CloudFormation...")
    waiter.wait(StackName=STACK_NAME)

    print("Infrastructure deployed successfully!")


def print_stack_outputs(cf):
    response = cf.describe_stacks(StackName=STACK_NAME)

    for output in response["Stacks"][0].get("Outputs", []):
        print(f"{output['OutputKey']}: {output['OutputValue']}")


def main():
    session = boto3.Session(
        profile_name=AWS_PROFILE,
        region_name=AWS_REGION
    )

    s3 = session.client("s3")
    cf = session.client("cloudformation")

    zip_path, s3_key = create_lambda_package()

    upload_lambda_package(
        s3=s3,
        zip_path=zip_path,
        s3_key=s3_key
    )

    deploy_stack(
        cf=cf,
        s3_key=s3_key
    )

    print_stack_outputs(cf)


if __name__ == "__main__":
    main()