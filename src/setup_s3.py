
import boto3
import time

REGION = "eu-west-1"
PROFILE = "cda-dev"


def main():
    session = boto3.Session(
        profile_name=PROFILE,
        region_name=REGION
    )

    s3 = session.client("s3")

    bucket_name = f"cloud-document-analyzer-{int(time.time())}"

    print(f"Creating bucket: {bucket_name}")

    # 1. Create bucket
    s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={
            "LocationConstraint": REGION
        }
    )

    # 2. Block public access
    s3.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True
        }
    )

    # 3. Enable default encryption
    s3.put_bucket_encryption(
        Bucket=bucket_name,
        ServerSideEncryptionConfiguration={
            "Rules": [
                {
                    "ApplyServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "AES256"
                    }
                }
            ]
        }
    )

    print("\nBucket successfully created!")
    print(f"Bucket name: {bucket_name}")
    print(f"Region: {REGION}")


if __name__ == "__main__":
    main()
