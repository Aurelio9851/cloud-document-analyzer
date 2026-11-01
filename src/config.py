import json
import os

AWS_PROFILE = "cda-dev"
AWS_REGION = "eu-west-1"

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATA_DIR = os.path.join(PROJECT_ROOT, "docs")

STATE_PATH = os.path.join(
    PROJECT_ROOT,
    "build",
    "deployment_state.json"
)

with open(STATE_PATH, "r", encoding="utf-8") as file:
    deployment_state = json.load(file)

S3_BUCKET_NAME = deployment_state["bucket_name"]