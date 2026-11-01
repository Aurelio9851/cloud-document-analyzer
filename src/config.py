
import os

AWS_PROFILE = "cda-dev"
AWS_REGION = "eu-west-1"

S3_BUCKET_NAME = "cloud-document-analyzer-1793537371"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "docs")
