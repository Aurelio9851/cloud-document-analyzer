
import hashlib
import json
import os
import uuid
import zipfile

import boto3
from botocore.exceptions import ClientError

from config import (
    AWS_PROFILE,
    AWS_REGION,
    PROJECT_ROOT
)


STORAGE_STACK_NAME = "cloud-document-analyzer-storage-stack"
APP_STACK_NAME = "cloud-document-analyzer-stack"

INFRASTRUCTURE_DIR = os.path.join(
    PROJECT_ROOT,
    "infrastructure"
)

STORAGE_TEMPLATE_PATH = os.path.join(
    INFRASTRUCTURE_DIR,
    "storage.yaml"
)

LAMBDA_TEMPLATE_PATH = os.path.join(
    INFRASTRUCTURE_DIR,
    "lambda.yaml"
)

LAMBDA_SOURCE_DIR = os.path.join(
    PROJECT_ROOT,
    "src",
    "lambda_function"
)

BUILD_DIR = os.path.join(PROJECT_ROOT, "build")
STATE_PATH = os.path.join(BUILD_DIR, "deployment_state.json")


def load_or_create_bucket_name(session):
    """Retrieve the existing bucket name or generate a unique one."""

    os.makedirs(BUILD_DIR, exist_ok=True)

    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, "r", encoding="utf-8") as file:
            state = json.load(file)

        bucket_name = state["bucket_name"]
        print(f"Using existing bucket name: {bucket_name}")
        return bucket_name

    account_id = session.client("sts").get_caller_identity()["Account"]
    suffix = uuid.uuid4().hex[:8]

    bucket_name = f"cloud-document-analyzer-{account_id}-{suffix}"

    state = {
        "bucket_name": bucket_name
    }

    with open(STATE_PATH, "w", encoding="utf-8") as file:
        json.dump(state, file, indent=4)

    print(f"Generated bucket name: {bucket_name}")

    return bucket_name



def create_lambda_package():
    """Package all Lambda source files into a versioned ZIP archive."""

    os.makedirs(BUILD_DIR, exist_ok=True)

    temporary_zip = os.path.join(
        BUILD_DIR,
        "lambda_package_temp.zip"
    )

    with zipfile.ZipFile(
        temporary_zip,
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

    with open(temporary_zip, "rb") as file:
        package_hash = hashlib.sha256(file.read()).hexdigest()[:12]

    s3_key = f"deployments/lambda_package_{package_hash}.zip"

    zip_path = os.path.join(
        BUILD_DIR,
        f"lambda_package_{package_hash}.zip"
    )

    os.replace(temporary_zip, zip_path)

    print(f"Lambda package created: {zip_path}")
    print(f"Package SHA-256: {package_hash}")

    return zip_path, s3_key



def stack_exists(cf, stack_name):
    """Check whether a CloudFormation stack exists."""

    try:
        cf.describe_stacks(StackName=stack_name)
        return True

    except ClientError as error:
        if error.response["Error"]["Code"] == "ValidationError":
            return False
        raise


def deploy_stack(cf, stack_name, template_path, parameters):
    """Create or update a CloudFormation stack."""

    with open(template_path, "r", encoding="utf-8") as file:
        template_body = file.read()

    exists = stack_exists(cf, stack_name)

    if exists:
        print(f"\nUpdating stack: {stack_name}")

        try:
            cf.update_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Parameters=parameters,
                Capabilities=["CAPABILITY_NAMED_IAM"]
            )

            waiter = cf.get_waiter("stack_update_complete")

        except ClientError as error:
            if "No updates are to be performed" in str(error):
                print("No CloudFormation changes required.")
                return

            raise

    else:
        print(f"\nCreating stack: {stack_name}")

        cf.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=parameters,
            Capabilities=["CAPABILITY_NAMED_IAM"]
        )

        waiter = cf.get_waiter("stack_create_complete")

    print("Waiting for CloudFormation...")
    waiter.wait(StackName=stack_name)

    print(f"Stack deployed successfully: {stack_name}")


def upload_lambda_package(s3, bucket_name, zip_path, s3_key):
    """Upload the Lambda deployment package to S3."""

    print(f"\nUploading package to s3://{bucket_name}/{s3_key}")

    s3.upload_file(
        zip_path,
        bucket_name,
        s3_key,
        ExtraArgs={
            "ServerSideEncryption": "AES256"
        }
    )

    print("Lambda package uploaded successfully.")


def get_stack_output(cf, stack_name, output_key):
    """Retrieve a CloudFormation stack output."""

    response = cf.describe_stacks(StackName=stack_name)

    outputs = response["Stacks"][0].get("Outputs", [])

    for output in outputs:
        if output["OutputKey"] == output_key:
            return output["OutputValue"]

    raise RuntimeError(
        f"Output '{output_key}' not found in stack '{stack_name}'."
    )


def main():

    session = boto3.Session(
        profile_name=AWS_PROFILE,
        region_name=AWS_REGION
    )

    s3 = session.client("s3")
    cf = session.client("cloudformation")

    bucket_name = load_or_create_bucket_name(session)

    # Phase 1: Create the S3 bucket.
    deploy_stack(
        cf=cf,
        stack_name=STORAGE_STACK_NAME,
        template_path=STORAGE_TEMPLATE_PATH,
        parameters=[
            {
                "ParameterKey": "S3BucketName",
                "ParameterValue": bucket_name
            },
            {
                "ParameterKey": "LambdaFunctionArn",
                "ParameterValue": ""
            }
        ]
    )

    # Phase 2: Build and upload the Lambda package.
    zip_path, s3_key = create_lambda_package()

    upload_lambda_package(
        s3=s3,
        bucket_name=bucket_name,
        zip_path=zip_path,
        s3_key=s3_key
    )

    # Phase 3: Deploy Lambda infrastructure.
    deploy_stack(
        cf=cf,
        stack_name=APP_STACK_NAME,
        template_path=LAMBDA_TEMPLATE_PATH,
        parameters=[
            {
                "ParameterKey": "S3BucketName",
                "ParameterValue": bucket_name
            },
            {
                "ParameterKey": "LambdaCodeS3Key",
                "ParameterValue": s3_key
            }
        ]
    )

    # Retrieve the deployed Lambda ARN.
    lambda_arn = get_stack_output(
        cf,
        APP_STACK_NAME,
        "LambdaFunctionArn"
    )

    # Phase 4: Configure S3 -> Lambda notifications.
    deploy_stack(
        cf=cf,
        stack_name=STORAGE_STACK_NAME,
        template_path=STORAGE_TEMPLATE_PATH,
        parameters=[
            {
                "ParameterKey": "S3BucketName",
                "ParameterValue": bucket_name
            },
            {
                "ParameterKey": "LambdaFunctionArn",
                "ParameterValue": lambda_arn
            }
        ]
    )

    print("\nDeployment completed successfully.")
    print(f"S3 bucket: {bucket_name}")
    print(f"Lambda ARN: {lambda_arn}")


if __name__ == "__main__":
    main()
