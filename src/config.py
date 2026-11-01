import os

AWS_PROFILE = "cda-dev"
AWS_REGION = "eu-west-1"

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATA_DIR = os.path.join(PROJECT_ROOT, "docs")